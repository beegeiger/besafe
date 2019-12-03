import React from 'react';
import { ContactForm } from './Components/contactform';
import { Form } from 'antd';



class App extends React.Component {
   render() {
      return (
         <div>
            <p>Lets See if This Works! This is being rendered from app.js</p>
            <ContactForm />
         </div>
      );
   }
}
export default App;