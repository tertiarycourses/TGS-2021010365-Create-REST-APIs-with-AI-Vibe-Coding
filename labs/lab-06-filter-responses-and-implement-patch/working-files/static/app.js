const state = { products: [], customers: [], orders: [] };
const money = new Intl.NumberFormat("en-SG", { style: "currency", currency: "SGD" });
const statusNode = document.querySelector("#status");

function apiKey() { return document.querySelector("#api-key").value.trim(); }
function setStatus(message, type = "") { statusNode.textContent = message; statusNode.className = `status ${type}`; }

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const hasJson = (response.headers.get("content-type") || "").includes("application/json");
  const body = hasJson ? await response.json() : null;
  if (!response.ok) {
    const issue = body?.error?.message || body?.detail?.[0]?.msg || `Request failed (${response.status})`;
    throw new Error(issue);
  }
  return body;
}

function writeOptions(select, records, label) {
  select.replaceChildren();
  records.forEach(record => {
    const option = document.createElement("option");
    option.value = record.id;
    option.textContent = label(record);
    select.append(option);
  });
}

function renderProducts() {
  const host = document.querySelector("#product-list");
  const template = document.querySelector("#product-template");
  host.replaceChildren();
  document.querySelector("#product-count").textContent = `${state.products.length} products`;
  state.products.forEach((product, index) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.querySelector(".product-visual").textContent = ["◒", "◫", "◇", "⌁"][index % 4];
    node.querySelector(".product-sku").textContent = product.sku;
    node.querySelector(".product-name").textContent = product.name;
    node.querySelector(".product-price").textContent = money.format(Number(product.price));
    node.querySelector(".product-stock").textContent = `${product.stock_quantity} in stock`;
    node.querySelector(".product-status").textContent = product.status;
    host.append(node);
  });
  writeOptions(document.querySelector("#order-product"), state.products.filter(p => p.status === "active" && p.stock_quantity > 0), p => `${p.name} · ${p.stock_quantity} available`);
}

function renderCustomers() {
  const host = document.querySelector("#customer-list");
  host.replaceChildren(...state.customers.slice(0, 6).map(customer => {
    const article = document.createElement("article");
    article.innerHTML = `<span>${customer.name.slice(0, 1).toUpperCase()}</span><div><strong></strong><small></small></div>`;
    article.querySelector("strong").textContent = customer.name;
    article.querySelector("small").textContent = customer.company || customer.email;
    return article;
  }));
  writeOptions(document.querySelector("#order-customer"), state.customers, c => `${c.name} · ${c.email}`);
}

function renderOrders() {
  const host = document.querySelector("#order-list");
  host.replaceChildren(...state.orders.slice(0, 6).map(order => {
    const article = document.createElement("article");
    article.innerHTML = `<span>#${order.id}</span><div><strong></strong><small></small></div>`;
    article.querySelector("strong").textContent = `${order.customer_name} · ${money.format(Number(order.total))}`;
    article.querySelector("small").textContent = `${order.items.length} line item(s) · ${order.status}`;
    return article;
  }));
}

async function loadAll() {
  try {
    setStatus("Loading live API data…");
    const [summary, products, customers, orders] = await Promise.all([
      api("/api/v1/dashboard"), api("/api/v1/products"), api("/api/v1/customers"), api("/api/v1/orders")
    ]);
    state.products = products.items; state.customers = customers; state.orders = orders;
    document.querySelector("#kpi-products").textContent = summary.products;
    document.querySelector("#kpi-customers").textContent = summary.customers;
    document.querySelector("#kpi-orders").textContent = summary.orders;
    document.querySelector("#kpi-revenue").textContent = money.format(Number(summary.revenue));
    renderProducts(); renderCustomers(); renderOrders();
    setStatus(`API synchronized · ${summary.low_stock} low-stock product(s).`, "success");
  } catch (error) { setStatus(error.message, "error"); }
}

document.querySelector("#product-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = { sku: document.querySelector("#sku").value.trim().toUpperCase(), name: document.querySelector("#product-name").value.trim(), price: Number(document.querySelector("#price").value), stock_quantity: Number(document.querySelector("#stock").value), status: "active" };
  try {
    await api("/api/v1/products", { method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": apiKey() }, body: JSON.stringify(payload) });
    form.reset(); setStatus("Product created with HTTP 201.", "success"); await loadAll();
  } catch (error) { setStatus(error.message, "error"); }
});

document.querySelector("#customer-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = { name: document.querySelector("#customer-name").value.trim(), email: document.querySelector("#customer-email").value.trim(), company: document.querySelector("#customer-company").value.trim() };
  try {
    await api("/api/v1/customers", { method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": apiKey() }, body: JSON.stringify(payload) });
    form.reset(); setStatus("CRM customer created with HTTP 201.", "success"); await loadAll();
  } catch (error) { setStatus(error.message, "error"); }
});

document.querySelector("#order-form").addEventListener("submit", async event => {
  event.preventDefault();
  const payload = { customer_id: Number(document.querySelector("#order-customer").value), items: [{ product_id: Number(document.querySelector("#order-product").value), quantity: Number(document.querySelector("#order-quantity").value) }] };
  try {
    await api("/api/v1/orders", { method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": apiKey() }, body: JSON.stringify(payload) });
    setStatus("Order created atomically with HTTP 201.", "success"); await loadAll();
  } catch (error) { setStatus(error.message, "error"); }
});

document.querySelector("#refresh").addEventListener("click", loadAll);
loadAll();
