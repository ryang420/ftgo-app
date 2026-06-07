import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import ConsumerSetupModal from "./components/ConsumerSetupModal.jsx";
import useConsumerSession from "./hooks/useConsumerSession.js";
import RestaurantListPage from "./pages/RestaurantListPage.jsx";
import RestaurantDetailPage from "./pages/RestaurantDetailPage.jsx";
import OrderStatusPage from "./pages/OrderStatusPage.jsx";
import MyOrdersPage from "./pages/MyOrdersPage.jsx";
import KitchenDashboardPage from "./pages/KitchenDashboardPage.jsx";
import OperationsPage from "./pages/OperationsPage.jsx";
import ConsumerLookupPage from "./pages/ConsumerLookupPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

function App() {
  const { session } = useConsumerSession();

  return (
    <>
      <NavBar />
      {!session && <ConsumerSetupModal mode="banner" />}
      <Routes>
        <Route path="/orders/by-consumer" element={<ConsumerLookupPage />} />
        <Route path="/orders/:orderId" element={<OrderStatusPage />} />
        <Route path="/my-orders" element={<MyOrdersPage />} />
        <Route path="/kitchen" element={<KitchenDashboardPage />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantDetailPage />} />
        <Route path="/" element={<RestaurantListPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}

export default App;
