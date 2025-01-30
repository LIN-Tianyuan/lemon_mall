let vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法
    delimiters: ['[[', ']]'],
    data: {
        username: '',
        password: '',

        error_username: false,
        error_password: false,
        remembered: false,
    },
    methods: {
        // check username
        check_username(){
        	let re = /^[+a-zA-Z0-9_-]{5,20}$/;
			if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username = true;
            }
        },
		// check password
        check_password(){
        	let re = /^[0-9A-Za-z]{8,20}$/;
			if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // form submission
        on_submit(){
            this.check_username();
            this.check_password();

            if (this.error_username == true || this.error_password == true) {
                // Login conditions not met: disable form
				window.event.returnValue = false
            }
        },
        // qq login
        qq_login(){
            let next = get_query_string('next') || '/';
            let url = '/qq/login/?next=' + next;
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    location.href = response.data.login_url;
                })
                .catch(error => {
                    console.log(error.response);
                })
        }
    }
});