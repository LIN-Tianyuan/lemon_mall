
// Creating Vue Objects vm
let vm = new Vue({
    el: '#app', // Finding bound HTML content by ID selector
    // Changing the syntax for reading variables in Vue
    delimiters: ['[[', ']]'],
    data: { // data object
        // v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url: '',
        uuid: '',
        image_code: '',
        sms_code_tip: '获取短信验证码',
        send_flag: false, // Analogous to going to the bathroom, send_flag is the lock, false means the door is open, true means the door is closed.
        sms_code: '',

        // v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        // error_message
        error_name_message: '',
        error_mobile_message: '',
        error_image_code_message: '',
        error_sms_code_message: '',
    },
    mounted() { // that will be called after the page loads
        // Generate graphical CAPTCHA
        this.generate_image_code();
    },
    methods: { // 定义和实现事件方法
        // 发送短信验证码
        send_sms_code() {
            // 避免恶意用户频繁的点击获取短信验证码的标签
            if (this.send_flag == true) { // 先判断是否有人正在上厕所
                return; // 有人正在上厕所，退回去
            }
            this.send_flag = true; // 如果可以进入到厕所，立即关门

            // 校验数据：mobile，image_code
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true) {
                this.send_flag = false;
                return;
            }

            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // 展示倒计时60秒效果
                        let num = 60;
                        let t = setInterval(() => {
                            if (num == 1) { // 倒计时即将结束
                                clearInterval(t); // 停止回调函数的执行
                                this.sms_code_tip = '获取短信验证码'; // 还原sms_code_tip的提示文字
                                this.generate_image_code(); // 重新生成图形验证码
                                this.send_flag = false;
                            } else { // 正在倒计时
                                num -= 1; // num = num - 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    } else {
                        if (response.data.code == '4001') { // 图形验证码错误
                            this.error_image_code_message = response.data.errmsg;
                            this.error_image_code = true;
                        } else { // 4002 短信验证码错误
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.send_flag = false;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.send_flag = false;
                })
        },
        // 生成图形验证码的方法：封装的思想，代码复用
        generate_image_code() {
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },
        // Check username
        check_username() {
            // Username is 5-20 characters，[a-zA-Z0-9_-]
            // Define Regular
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            // Match Username Data with Regulars
            if (re.test(this.username)) {
                // Match successful, do not show error message
                this.error_name = false;
            } else {
                // Match failed, display error message
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }

            // Determine whether a user name is a duplicate registration
            if (this.error_name == false) { // Go back to judgment only if the user name entered by the user satisfies the condition
                let url = '/usernames/' + this.username + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            // Username already exists
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        } else {
                            // User name does not exist
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // 校验密码
        check_password() {
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 校验确认密码
        check_password2() {
            if (this.password != this.password2) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },
        // 校验手机号
        check_mobile() {
            let re = /^\+?(\d{1,3})?[- ]?(\d{10,11})$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }

            // 判断手机号是否重复注册
            if (this.error_mobile == false) {
                let url = '/mobiles/'+ this.mobile + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        } else {
                            this.error_mobile = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // 校验图形验证码吗
        check_image_code() {
            if (this.image_code.length != 4) {
                this.error_image_code_message = '请输入图形验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        // 校验短信验证码
        check_sms_code(){
            if(this.sms_code.length != 6){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        // 校验是否勾选协议
        check_allow() {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 监听表单提交事件
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_sms_code();
            this.check_allow();

            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if (this.error_name == true || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_sms_code == true || this.error_allow == true) {
                // 禁用掉表单的提交事件
                window.event.returnValue = false;
            }
        },
    }
});