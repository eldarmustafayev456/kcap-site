'use strict';
// Integration: remove the mailto submit handler before attaching this replacement.
function attachKcapDirectEnquiry(form, endpoint, policyVersion) {
  const url = new URL(endpoint);
  if (url.protocol !== 'https:' || !policyVersion) throw new Error('Approved endpoint and notice version required');
  const language = form.dataset.language;
  const copy = {
    en: {busy:'Sending…', success:'Thank you. Your enquiry has been submitted.', error:'Sending could not be confirmed. Please contact us by email.', rate:'Too many attempts. Please wait before trying again.'},
    ko: {busy:'전송 중…', success:'감사합니다. 문의가 접수되었습니다.', error:'전송을 확인할 수 없습니다. 이메일로 문의해 주세요.', rate:'요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.'},
    ru: {busy:'Отправляем…', success:'Спасибо. Ваше обращение отправлено.', error:'Отправку не удалось подтвердить. Свяжитесь с нами по электронной почте.', rate:'Слишком много попыток. Подождите перед повторной отправкой.'}
  }[language];
  if (!copy || !form.elements.namedItem('privacy_consent') || !form.elements.namedItem('website')) throw new Error('Approved consent field and spam trap required');
  const button = form.querySelector('button[type=submit]');
  const status = form.querySelector('[role=status]');
  if (!button || !status) throw new Error('Submit button and accessible status region required');
  let busy = false;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;
    const input = new FormData(form);
    const payload = {name:input.get('name'), organisation:input.get('organisation'), email:input.get('email'), topic:input.get('topic'), message:input.get('message'), project_id:input.get('project_id') || '', language, website:input.get('website') || '', consent:form.elements.namedItem('privacy_consent').checked, consent_version:policyVersion};
    if (!payload.consent) return;
    busy = true; button.disabled = true; status.textContent = copy.busy; form.setAttribute('aria-busy','true');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(url.href, {method:'POST', credentials:'omit', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload), signal:controller.signal});
      const result = await response.json();
      if (response.status === 202 && result.ok === true && result.code === 'queued') {
        status.textContent = copy.success;
        form.elements.namedItem('message').value = '';
        form.elements.namedItem('privacy_consent').checked = false;
      } else status.textContent = response.status === 429 ? copy.rate : copy.error;
    } catch (_) { status.textContent = copy.error; }
    finally { clearTimeout(timer); busy = false; button.disabled = false; form.removeAttribute('aria-busy'); }
  });
}
