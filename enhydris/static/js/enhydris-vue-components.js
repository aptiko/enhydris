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

const i18n = new VueI18n({
  locale: enhydris.activeTranslation,
  messages,
});

const vueStore = {
  loggedOnUser: enhydris.loggedOnUser,
};

Vue.component('DashboardButton', {
  data() {
    return { sharedState: vueStore };
  },
  template: `
    <b-nav-item v-if="sharedState.loggedOnUser" href="/admin/">
      {{ $t("Dashboard") }}
    </b-nav-item>
  `,
});

Vue.component('LoginButton', {
  data() {
    return {
      sharedState: vueStore,
      loggingOut: false,
    };
  },
  template: `
      <b-nav-item v-if="sharedState.loggedOnUser" v-on:click="logout">
        <b-spinner v-if="loggingOut"></b-spinner>
        {{ $t("Logout") }}
      </b-nav-item>
      <b-nav-item v-else v-b-modal.login-form>
        {{ $t("Login") }}
        <LoginForm/>
      </b-nav-item>
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
  },
});

Vue.component('LoginForm', {
  data() {
    return {
      sharedState: vueStore,
      errors: '',
      username: '',
      password: '',
    };
  },
  template: `
  <div>
    <b-modal id="login-form" :title="$t('Login')" @ok="doLogin" :ok-title="$t('Login')" :cancel-title="$t('Cancel')">
      <p v-if="errors" class="text-danger">{{ errors }}</p>
      <b-form-input v-model="username" :placeholder="$t('Username')"></b-form-input>
      <b-form-input v-model="password" type="password" :placeholder="$t('Password')"></b-form-input>
    </b-modal>
   </div>
  `,
  methods: {
    doLogin(bvModalEvent) {
      bvModalEvent.preventDefault();
      const that = this;
      axios.post('/api/auth/login/', { username: that.username, password: that.password })
        .then(function () {
          that.sharedState.loggedOnUser = that.username;
          that.$bvModal.hide('login-form');
        })
        .catch(function (error) {
          [that.errors] = error.response.data.non_field_errors;
        });
    },
  },
});

const app = new Vue({
  i18n,
  el: 'user-menu-items',
  template: '<b-navbar-nav class="ml-auto"><DashboardButton/><LoginButton/></b-navbar-nav>',
  data() {
    return { sharedState: vueStore };
  },
});
