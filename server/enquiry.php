<?php
// KCAP direct enquiry handler. Private configuration is stored outside the document root.
declare(strict_types=1);
function respond(int $status, string $code): void {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode(['ok' => $status === 202, 'code' => $code]);
    exit;
}
if (($_SERVER['HTTPS'] ?? '') !== 'on') respond(426, 'https_required');
header('X-Content-Type-Options: nosniff');
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== 'https://www.koreacentralasia.com') respond(403, 'origin');
header('Access-Control-Allow-Origin: https://www.koreacentralasia.com');
header('Vary: Origin');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { http_response_code(204); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') respond(405, 'method');
if (!(strpos(strtolower($_SERVER['CONTENT_TYPE'] ?? ''), 'application/json') === 0)) respond(415, 'format');
$configFile = dirname(__DIR__) . '/kcap-form-private/config.php';
if (!$configFile || !is_file($configFile)) respond(503, 'not_configured');
$rootPath = realpath($_SERVER['DOCUMENT_ROOT'] ?? '');
$configPath = realpath($configFile);
if (!$rootPath || !$configPath || (strpos($configPath, rtrim($rootPath, DIRECTORY_SEPARATOR).DIRECTORY_SEPARATOR) === 0)) respond(503, 'not_configured');
$config = require $configFile; // This file must be outside the public document root.
if (!is_array($config) || empty($config['enabled']) || empty($config['state_dir']) || empty($config['rate_key']) || empty($config['consent_version'])) respond(503, 'not_configured');
if (!function_exists('mail')) respond(503, 'transport_unavailable');
$raw = file_get_contents('php://input', false, null, 0, 40001);
if ($raw === false || strlen($raw) > 40000) respond(413, 'size');
try { $data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR); }
catch (JsonException $e) { respond(400, 'invalid_json'); }
if (!is_array($data)) respond(400, 'invalid_json');
$limits = ['name'=>200,'organisation'=>200,'email'=>254,'topic'=>20,'message'=>20000,'language'=>2,'project_id'=>32,'website'=>200,'consent_version'=>80];
foreach ($limits as $field=>$limit) {
    if (isset($data[$field]) && !is_string($data[$field])) respond(422, 'fields');
    if (strlen($data[$field] ?? '') > $limit) respond(422, 'fields');
}
if (trim($data['website'] ?? '') !== '') respond(422, 'spam');
foreach (['name','organisation','email','message','topic','language','consent_version'] as $field) if (trim($data[$field] ?? '') === '') respond(422, 'fields');
if (!in_array($data['topic'], ['general','project'], true) || !in_array($data['language'], ['en','ko','ru'], true)) respond(422, 'fields');
if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n]/', $data['email'])) respond(422, 'email');
if (($data['consent'] ?? null) !== true || !hash_equals($config['consent_version'], $data['consent_version'])) respond(422, 'consent');
$project = trim($data['project_id'] ?? '');
if ($project !== '' && !in_array($project, $config['published_project_ids'] ?? [], true)) respond(422, 'project');
$state = realpath($config['state_dir']);
if (!$state || strlen($config['rate_key']) < 32 || (strpos($state, rtrim($rootPath, DIRECTORY_SEPARATOR).DIRECTORY_SEPARATOR) === 0)) respond(503, 'not_configured');
if (!is_dir($state) || !is_writable($state)) respond(503, 'state_unavailable');
$now = time();
$ipKey = hash_hmac('sha256', $_SERVER['REMOTE_ADDR'] ?? '', $config['rate_key']);
$lock = fopen($state . '/rate-lock', 'c');
if (!$lock || !flock($lock, LOCK_EX)) respond(503, 'state_unavailable');
$rateFile = $state . '/rates.json';
$rates = is_file($rateFile) ? json_decode((string)file_get_contents($rateFile), true) : [];
if (!is_array($rates)) $rates = [];
foreach ($rates as $key => $times) {
    $rates[$key] = array_values(array_filter((array)$times, fn($t) => is_int($t) && $t > $now-600));
    if (!$rates[$key]) unset($rates[$key]);
}
if (count($rates[$ipKey] ?? []) >= 5) {
    flock($lock, LOCK_UN); fclose($lock); header('Retry-After: 600'); respond(429, 'rate');
}
$rates[$ipKey][] = $now;
if (file_put_contents($rateFile, json_encode($rates)) === false) { flock($lock, LOCK_UN); fclose($lock); respond(503, 'state_unavailable'); }
flock($lock, LOCK_UN); fclose($lock);
$topic = $project !== '' ? 'project' : $data['topic'];
$to = $topic === 'project' ? 'project@koreacentralasia.com' : 'info@koreacentralasia.com';
$subject = 'KCAP website enquiry' . ($project !== '' ? ' - '.$project : '');
$body = implode("\n", ['Language: '.$data['language'], 'Project: '.($project ?: '-'), 'Name: '.$data['name'], 'Organisation: '.$data['organisation'], 'Email: '.$data['email'], 'Consent version: '.$data['consent_version'], 'Received UTC: '.gmdate('c'), 'Retention: 12 months after the last substantive exchange', '', $data['message']]);
$headers = ['From'=>'KCAP website <info@koreacentralasia.com>', 'Reply-To'=>$data['email'], 'MIME-Version'=>'1.0', 'Content-Type'=>'text/plain; charset=UTF-8', 'X-Mailer'=>'KCAP'];
// Transport acceptance is not proof of inbox delivery. Verify both inboxes before activation.
if (!mail($to, $subject, $body, $headers)) respond(503, 'delivery');
respond(202, 'queued');
