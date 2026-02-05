import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import VocabularyList from './pages/vocabulary/VocabularyList';
import AddVocabulary from './pages/vocabulary/AddVocabulary';
import EditVocabulary from './pages/vocabulary/EditVocabulary';
import ReviewSession from './pages/vocabulary/ReviewSession';
import { useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Đang tải...</div>;
  if (!user) return <Navigate to="/login" />;

  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="vocabulary" element={<VocabularyList />} />
          <Route path="vocabulary/new" element={<AddVocabulary />} />
          <Route path="vocabulary/:id/edit" element={<EditVocabulary />} />
          <Route path="vocabulary/review" element={<ReviewSession />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router >
  );
}

export default App;
