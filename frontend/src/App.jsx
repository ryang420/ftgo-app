import { Navigate, Route, Routes } from "react-router-dom";
import RestaurantListPage from "./pages/RestaurantListPage.jsx";
import RestaurantDetailPage from "./pages/RestaurantDetailPage.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<RestaurantListPage />} />
      <Route path="/restaurants/:restaurantId" element={<RestaurantDetailPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
