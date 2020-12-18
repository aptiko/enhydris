enhydris.VueApp = {
};

const app = Vue.createApp(enhydris.VueApp);

app.component('user-menu-items', {
  template: '<li><a class="nav-link" href="#">Login</a></li>',
});

app.mount('body');
