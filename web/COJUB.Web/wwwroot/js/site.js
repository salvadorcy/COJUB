document.querySelector('[data-menu]')?.addEventListener('click',()=>document.querySelector('#sidebar')?.classList.toggle('open'));
document.querySelectorAll('[data-confirm]').forEach(button=>button.addEventListener('click',event=>{if(!window.confirm(button.dataset.confirm||'Confirmar aquesta acció?'))event.preventDefault();}));
const current=window.location.pathname;
document.querySelectorAll('.main-nav a').forEach(link=>{const href=link.getAttribute('href');if(href&&href!=='/'&&current.startsWith(href))link.classList.add('active');else if(current==='/'&&href==='/')link.classList.add('active');});
