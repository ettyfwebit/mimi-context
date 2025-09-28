
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { SearchPage } from '@/pages/Search';
import { ChatPage } from '@/pages/Chat';
import { StudioPage } from '@/pages/Studio';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/search" replace />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="studio" element={<StudioPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
