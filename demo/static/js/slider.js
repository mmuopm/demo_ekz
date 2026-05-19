// окно подтверждения перед сменой статуса
document.querySelectorAll('form[data-status-form]').forEach((form) => {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const modalEl = document.getElementById('statusModal');
    if (!modalEl) {
      form.submit();
      return;
    }
    const body = document.getElementById('statusModalBody');
    if (body) {
      body.textContent = 'Сменить статус заявки №' + form.dataset.bookingId + '?';
    }
    const confirmBtn = document.getElementById('confirmStatusBtn');
    if (confirmBtn) {
      confirmBtn.onclick = () => form.submit();
    }
    bootstrap.Modal.getOrCreateInstance(modalEl).show();
  });
});
