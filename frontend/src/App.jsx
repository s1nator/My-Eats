import { useEffect, useMemo, useState } from "react";

import {
  cancelOrder,
  changeOrderStatus,
  createOrder,
  getMenu,
  getOrders,
} from "./api";

const statusLabels = {
  CREATED: "Создан",
  COOKING: "Готовится",
  DELIVERING: "В пути",
  COMPLETED: "Завершён",
  CANCELLED: "Отменён",
};

const orderStatuses = Object.keys(statusLabels);

function formatPrice(value) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function App() {
  const [menu, setMenu] = useState([]);
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [orderFilter, setOrderFilter] = useState("");
  const [form, setForm] = useState({
    customer_name: "",
    customer_phone: "",
    delivery_address: "",
  });
  const [catalogError, setCatalogError] = useState("");
  const [orderError, setOrderError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isMenuLoading, setIsMenuLoading] = useState(true);
  const [isOrderLoading, setIsOrderLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    getMenu({ is_available: true })
      .then((items) => {
        if (!isCurrent) {
          return;
        }
        setCategories([...new Set(items.map((item) => item.category))]);
      })
      .catch(() => {
        if (isCurrent) {
          setCatalogError("Не удалось получить список категорий");
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  useEffect(() => {
    let isCurrent = true;
    setIsMenuLoading(true);
    setCatalogError("");

    getMenu({ category, is_available: true })
      .then((items) => {
        if (isCurrent) {
          setMenu(items);
        }
      })
      .catch((error) => {
        if (isCurrent) {
          setCatalogError(error.message);
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsMenuLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [category]);

  function loadOrders(status = orderFilter) {
    setIsOrderLoading(true);
    setOrderError("");

    return getOrders(status)
      .then(setOrders)
      .catch((error) => setOrderError(error.message))
      .finally(() => setIsOrderLoading(false));
  }

  useEffect(() => {
    loadOrders(orderFilter);
  }, [orderFilter]);

  const total = useMemo(
    () => cart.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0),
    [cart],
  );

  function addToCart(item) {
    setCart((currentCart) => {
      const existingItem = currentCart.find((cartItem) => cartItem.id === item.id);

      if (existingItem) {
        return currentCart.map((cartItem) =>
          cartItem.id === item.id
            ? { ...cartItem, quantity: cartItem.quantity + 1 }
            : cartItem,
        );
      }

      return [...currentCart, { ...item, quantity: 1 }];
    });
  }

  function changeQuantity(itemId, delta) {
    setCart((currentCart) =>
      currentCart
        .map((item) =>
          item.id === itemId ? { ...item, quantity: item.quantity + delta } : item,
        )
        .filter((item) => item.quantity > 0),
    );
  }

  async function submitOrder(event) {
    event.preventDefault();
    setOrderError("");
    setSuccessMessage("");

    if (cart.length === 0) {
      setOrderError("Добавь хотя бы одно блюдо в корзину");
      return;
    }

    setIsSubmitting(true);

    try {
      const order = await createOrder({
        ...form,
        items: cart.map((item) => ({
          menu_item_id: item.id,
          quantity: item.quantity,
        })),
      });
      setCart([]);
      setForm({ customer_name: "", customer_phone: "", delivery_address: "" });
      setSuccessMessage(`Заказ №${order.id} успешно создан`);
      setOrderFilter("");
      await loadOrders("");
    } catch (error) {
      setOrderError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function updateStatus(orderId, nextStatus) {
    setOrderError("");

    try {
      const updatedOrder = await changeOrderStatus(orderId, nextStatus);
      setOrders((currentOrders) =>
        currentOrders.map((order) => (order.id === orderId ? updatedOrder : order)),
      );
    } catch (error) {
      setOrderError(error.message);
    }
  }

  async function cancelExistingOrder(orderId) {
    setOrderError("");

    try {
      const updatedOrder = await cancelOrder(orderId);
      setOrders((currentOrders) =>
        currentOrders.map((order) => (order.id === orderId ? updatedOrder : order)),
      );
    } catch (error) {
      setOrderError(error.message);
    }
  }

  return (
    <main className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FOOD DELIVERY SERVICE</p>
          <h1>My Eats</h1>
          <p className="hero-text">Выбирай еду, оформляй заказ и следи за его статусом.</p>
        </div>
        <a className="cart-link" href="#checkout">
          Корзина <span>{cart.reduce((count, item) => count + item.quantity, 0)}</span>
        </a>
      </header>

      <section className="content-grid">
        <section className="catalog-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">МЕНЮ</p>
              <h2>Что будем есть?</h2>
            </div>
            <div className="filters" aria-label="Фильтр категорий">
              <button
                className={category === "" ? "filter active" : "filter"}
                onClick={() => setCategory("")}
                type="button"
              >
                Всё
              </button>
              {categories.map((itemCategory) => (
                <button
                  className={category === itemCategory ? "filter active" : "filter"}
                  key={itemCategory}
                  onClick={() => setCategory(itemCategory)}
                  type="button"
                >
                  {itemCategory}
                </button>
              ))}
            </div>
          </div>

          {catalogError && <p className="message error">{catalogError}</p>}
          {isMenuLoading && <p className="empty-state">Загружаем меню...</p>}
          {!isMenuLoading && !catalogError && menu.length === 0 && (
            <p className="empty-state">В этой категории пока нет доступных блюд.</p>
          )}

          <div className="menu-grid">
            {menu.map((item) => (
              <article className="menu-card" key={item.id}>
                <div className="menu-image">
                  {item.image_url ? (
                    <img alt={item.title} src={item.image_url} />
                  ) : (
                    <span>🍽️</span>
                  )}
                </div>
                <div className="menu-card-body">
                  <p className="category-label">{item.category}</p>
                  <h3>{item.title}</h3>
                  <p className="description">{item.description || "Описание появится позже."}</p>
                  <div className="menu-card-footer">
                    <strong>{formatPrice(item.price)}</strong>
                    <button className="primary-button" onClick={() => addToCart(item)} type="button">
                      В корзину
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="cart-panel" id="checkout">
          <div className="section-heading compact">
            <div>
              <p className="eyebrow">ЗАКАЗ</p>
              <h2>Корзина</h2>
            </div>
          </div>

          {cart.length === 0 ? (
            <p className="empty-state">Корзина пока пуста.</p>
          ) : (
            <ul className="cart-list">
              {cart.map((item) => (
                <li className="cart-item" key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <span>{formatPrice(item.price)}</span>
                  </div>
                  <div className="quantity-control">
                    <button aria-label={`Убрать ${item.title}`} onClick={() => changeQuantity(item.id, -1)} type="button">−</button>
                    <span>{item.quantity}</span>
                    <button aria-label={`Добавить ${item.title}`} onClick={() => changeQuantity(item.id, 1)} type="button">+</button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <div className="total-row">
            <span>Итого</span>
            <strong>{formatPrice(total)}</strong>
          </div>

          <form className="order-form" onSubmit={submitOrder}>
            <label>
              Имя
              <input
                name="customer_name"
                onChange={(event) => setForm({ ...form, customer_name: event.target.value })}
                required
                value={form.customer_name}
              />
            </label>
            <label>
              Телефон
              <input
                name="customer_phone"
                onChange={(event) => setForm({ ...form, customer_phone: event.target.value })}
                required
                type="tel"
                value={form.customer_phone}
              />
            </label>
            <label>
              Адрес доставки
              <textarea
                name="delivery_address"
                onChange={(event) => setForm({ ...form, delivery_address: event.target.value })}
                required
                rows="3"
                value={form.delivery_address}
              />
            </label>
            <button className="checkout-button" disabled={isSubmitting || cart.length === 0} type="submit">
              {isSubmitting ? "Оформляем..." : "Оформить заказ"}
            </button>
          </form>

          {successMessage && <p className="message success">{successMessage}</p>}
          {orderError && <p className="message error">{orderError}</p>}
        </aside>
      </section>

      <section className="orders-panel">
        <div className="section-heading orders-heading">
          <div>
            <p className="eyebrow">ИСТОРИЯ</p>
            <h2>Заказы</h2>
          </div>
          <select onChange={(event) => setOrderFilter(event.target.value)} value={orderFilter}>
            <option value="">Все статусы</option>
            {orderStatuses.map((orderStatus) => (
              <option key={orderStatus} value={orderStatus}>{statusLabels[orderStatus]}</option>
            ))}
          </select>
        </div>

        {isOrderLoading && <p className="empty-state">Загружаем заказы...</p>}
        {!isOrderLoading && orders.length === 0 && !orderError && (
          <p className="empty-state">Заказов пока нет.</p>
        )}

        <div className="orders-grid">
          {orders.map((order) => (
            <article className="order-card" key={order.id}>
              <div className="order-card-heading">
                <div>
                  <h3>Заказ №{order.id}</h3>
                  <p>{formatDate(order.created_at)}</p>
                </div>
                <span className={`status status-${order.status.toLowerCase()}`}>
                  {statusLabels[order.status]}
                </span>
              </div>
              <p className="order-customer">{order.customer_name} · {order.customer_phone}</p>
              <p className="order-address">{order.delivery_address}</p>
              <ul className="order-items">
                {order.items.map((item) => (
                  <li key={item.id}>Блюдо #{item.menu_item_id} × {item.quantity} — {formatPrice(item.price_at_order)}</li>
                ))}
              </ul>
              <div className="order-card-footer">
                <strong>{formatPrice(order.total_price)}</strong>
                <select
                  aria-label={`Статус заказа ${order.id}`}
                  onChange={(event) => updateStatus(order.id, event.target.value)}
                  value={order.status}
                >
                  {orderStatuses.map((orderStatus) => (
                    <option key={orderStatus} value={orderStatus}>{statusLabels[orderStatus]}</option>
                  ))}
                </select>
                {order.status !== "CANCELLED" && (
                  <button className="text-button" onClick={() => cancelExistingOrder(order.id)} type="button">
                    Отменить
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
