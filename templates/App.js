import React from 'react';
import { ContactForm } from './Components/contactform';
import { Contact } from './Components/contact';
import 'antd/dist/antd.css';



class App extends React.Component {
   render() {
      return (
         <div>
            <p>Lets See if This Works! This is being rendered from app.js</p>
            <ContactForm />
            <Contact />
         </div>
      );
   }
}
export default App;