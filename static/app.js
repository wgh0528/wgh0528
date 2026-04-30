async function fetchHistory() {
  const res = await fetch('/api/history');
  const data = await res.json();
  const box = document.getElementById('history');
  box.innerHTML = data.map(item => {
    if (item.type === 'images') {
      const imgs = item.items.map(u => `<a href="${u}" target="_blank">下载/查看</a>`).join(' | ');
      return `<div class="history-item"><b>${item.type}</b> ${item.created_at}<br/>${item.prompt}<br/>${imgs}</div>`;
    }
    return `<div class="history-item"><b>${item.type}</b> ${item.created_at}<br/>${item.result || ''}</div>`;
  }).join('');
}

document.getElementById('genBtn').onclick = async () => {
  const payload = {
    prompt: document.getElementById('prompt').value,
    style: document.getElementById('style').value,
    ratio: document.getElementById('ratio').value,
    count: parseInt(document.getElementById('count').value, 10),
  };
  const res = await fetch('/api/generate-images', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) return alert(data.error || '生成失败');

  const gallery = document.getElementById('gallery');
  gallery.innerHTML = data.items.map(u => `<div><img src="${u}"/><a href="${u}" download>下载</a></div>`).join('');
  await fetchHistory();
};

document.getElementById('videoBtn').onclick = async () => {
  const payload = {
    image_url: document.getElementById('videoImage').value,
    prompt: document.getElementById('videoPrompt').value,
  };
  const res = await fetch('/api/generate-video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) return alert(data.error || '生成失败');
  document.getElementById('videoResult').textContent = data.result;
  await fetchHistory();
};

fetchHistory();
