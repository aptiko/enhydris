const messages = {
  el: {
    Login: 'Είσοδος',
    Logout: 'Αποσύνδεση',
    Dashboard: 'Πίνακας ελέγχου',
    Username: 'Όνομα χρήστη',
    Password: 'Συνθηματικό',
    Cancel: 'Άκυρο',
  },
};

const i18n = VueI18n.createI18n({
  locale: enhydris.activeTranslation,
  messages,
});

const vueStore = {
  loggedOnUser: enhydris.loggedOnUser,
  loginFormVisible: false,
};

enhydris.VueApp = {
};

const app = Vue.createApp(enhydris.VueApp);
app.use(i18n);

app.component('user-menu-items', {
  data() {
    return { sharedState: vueStore };
  },
  template: '<DashboardButton/><LoginButton/>',
});

app.component('DashboardButton', {
  data() {
    return { sharedState: vueStore };
  },
  template: `
    <li v-if="sharedState.loggedOnUser">
      <a class="nav-link" href="/admin/">{{ $t("Dashboard") }}</a>
    </li>
  `,
});

app.component('LoginButton', {
  data() {
    return {
      sharedState: vueStore,
      loggingOut: false,
    };
  },
  template: `
    <li>
      <a v-if="sharedState.loggedOnUser" class="nav-link" href="#" v-on:click="logout">
        <span v-if="loggingOut" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ $t("Logout") }}
      </a>
      <a v-else class="nav-link" href="#" v-on:click="login">
        {{ $t("Login") }}
      </a>
    </li>
    <LoginForm/>
  `,
  methods: {
    logout() {
      this.loggingOut = true;
      axios.get('/admin/logout/')
        .then(() => {
          this.sharedState.loggedOnUser = '';
          this.loggingOut = false;
        })
        .catch(() => { this.loggingOut = false; });
    },
    login() {
      this.sharedState.loginFormVisible = true;
    },
  },
});

app.component('LoginForm', {
  data() {
    return {
      sharedState: vueStore,
      loginModal: null,
      errors: '',
      loggingIn: false,
    };
  },
  template: `
    <div id="login-form" class="modal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ $t("Login") }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" v-on:click="cancel"></button>
          </div>
          <div class="modal-body">
            <p v-if="errors" class="text-danger">{{ errors }}</p>
            <form>
              <div class="mb-3">
                <label for="username" class="form-label">{{ $t("Username") }}</label>
                <input type="text" class="form-control" id="username">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">{{ $t("Password") }}</label>
                <input type="password" class="form-control" id="password">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" v-on:click="cancel">{{ $t("Cancel") }}</button>
            <button type="button" class="btn btn-primary" v-on:click="doLogin">
              <span v-if="loggingIn" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ $t("Login") }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  mounted() {
    this.loginModal = new bootstrap.Modal(document.querySelector('#login-form'), {});
  },
  watch: {
    'sharedState.loginFormVisible': function () {
      if (this.sharedState.loginFormVisible) {
        this.loginModal.show();
      } else {
        this.loginModal.hide();
      }
    },
  },
  methods: {
    cancel() {
      this.sharedState.loginFormVisible = false;
    },
    doLogin() {
      const that = this;
      const username = document.querySelector('#username').value;
      const password = document.querySelector('#password').value;
      that.loggingIn = true;
      axios.post('/api/auth/login/', { username, password })
        .then(function () {
          that.sharedState.loggedOnUser = username;
          that.loggingIn = false;
          that.sharedState.loginFormVisible = false;
        })
        .catch(function (error) {
          that.loggingIn = false;
          [that.errors] = error.response.data.non_field_errors;
        });
    },
  },
});

app.mount('body');
