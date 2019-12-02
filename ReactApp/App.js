import React from 'react';
import { NavBar } from './Components/navbar';
import { ContactForm } from './Components/contactform';


class App extends React.Component {
   render() {
      return (
         <div>
            Lets See if This Works!
            <ContactForm />
         </div>
      );
   }
}
export default App;