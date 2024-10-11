
import { Route, Routes } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from './pages/Login';
import Signup from './pages/Signup';



function App() {
  console.log("App is rendering");
  return (
    
      <Routes>
        <Route path='/register' element={<Signup/>}/>
        <Route path='/login' element={<Login/>}/>
        

      </Routes>
  );
}

export default App;
