import React from 'react';
import ReactDOM from 'react-dom';
import 'antd/dist/antd.css';
import './index.css';
import { prefix } from "../urlprefix"
import {
  Form,
  Input,
  Tooltip,
  Icon,
  Cascader,
  Select,
  Row,
  Col,
  Checkbox,
  Button,
  AutoComplete,
} from 'antd';

const { Option } = Select;
const AutoCompleteOption = AutoComplete.Option;

export class ContactForm extends React.Component{
    handleSubmit(e) {
        e.preventDefault();
        var formData = new FormData(form)
        let uri = "prefix" + "/contacts"
        fetch(url, {
            method: 'post',
            body: formData,
        })
    }
    render() {
        return (
            <Form {...formItemLayout} onSubmit={this.handleSubmit}>
                <Form.Item label="Contact Name" >
                    {getFieldDecorator('nickname', {
                        rules: [{ required: true, message: 'Please input somke name!', whitespace: true }],
                    })(<Input />)}
                </Form.Item>
                <Form.Item label="E-mail">
                {getFieldDecorator('email', {
                    rules: [
                    {
                        type: 'email',
                        message: 'The input is not valid E-mail!',
                    },
                    {
                        required: false,
                        message: 'Please input contact E-mail!',
                    },
                    ],
                })(<Input />)}
                </Form.Item>
                <Form.Item label="Phone Number">
                    {getFieldDecorator('phone', {
                        rules: [{ required: false, message: 'Please input contact phone number!' }],
                    })(<Input addonBefore={prefixSelector} style={{ width: '100%' }} />)}
                </Form.Item>
                <Form.Item label="Message to Contact">
                    {getFieldDecorator('phone', {
                        rules: [{ required: true, message: 'Please input a message to your contact!' }],
                    })(<textarea rows="6" cols="50"></textarea>)}
                </Form.Item>
            </Form>
        )
    }
}