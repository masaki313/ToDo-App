const listEl = document.getElementById("list");
const formEl = document.getElementById("form");
const titleEl = document.getElementById("title");

async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let msg = "Request failed";
    try {
      const data = await res.json();
      msg = data.error || msg;
    } catch {}
    throw new Error(msg);
  }
  // 204などボディ無しの場合
  if (res.status === 204) return null;
  return res.json();
}

function render(tasks) {
  listEl.innerHTML = "";
  for (const t of tasks) {
    const li = document.createElement("li");
    li.className = "item";

    const left = document.createElement("div");
    left.className = "left";

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = !!t.done;
    cb.onchange = async () => {
      await api(`/api/tasks/${t.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ done: cb.checked }),
      });
      load();
    };

    const title = document.createElement("span");
    title.textContent = t.title;
    title.className = cb.checked ? "done" : "";

    left.appendChild(cb);
    left.appendChild(title);

    const del = document.createElement("button");
    del.textContent = "削除";
    del.className = "delete";
    del.onclick = async () => {
      await api(`/api/tasks/${t.id}`, { method: "DELETE" });
      load();
    };

    li.appendChild(left);
    li.appendChild(del);
    listEl.appendChild(li);
  }
}

async function load() {
  const tasks = await api("/api/tasks");
  render(tasks);
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = titleEl.value.trim();
  if (!title) return;

  try {
    await api("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    titleEl.value = "";
    load();
  } catch (err) {
    alert(err.message);
  }
});

load();