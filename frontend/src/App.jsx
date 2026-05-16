import { Navigate, Route, Routes } from "react-router-dom";
import RestaurantListPage from "./pages/RestaurantListPage.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<RestaurantListPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
