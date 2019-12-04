import { Menu } from 'antd';
import React from 'react';

export class NavBar extends React.Component {
    // handleClick = e => {
    //     console.log('click ', e);
    //     this.setState({
    //         current: e.key,
    //     });
    // };

    render() {
        return (
            <Menu onClick={this.handleClick} selectedKeys={[this.state.current]} mode="horizontal">
            <Menu.Item key="home">
              BeSafe Home
            </Menu.Item>
            <Menu.Item key="contacts">
              Contacts
            </Menu.Item>
            <Menu.Item key="profile">
              User Profile
            </Menu.Item>
            <Menu.Item key="login">
              Login
            </Menu.Item>
          </Menu>
        )
    }
}