import { FindingsProvider } from "./context/FindingsContext";
import FindingsList from "./pages/FindingsList";

function App() {
  return (
    // 여기서부터 하위 컴포넌트 전부가 findings 방송을 들을 수 있음
    <FindingsProvider>
      <FindingsList />
    </FindingsProvider>
  );
}

export default App;
