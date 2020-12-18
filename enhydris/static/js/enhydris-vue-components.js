const messages = {
  el: {
    Login: 'Είσοδος',
  },
};

const i18n = VueI18n.createI18n({
  locale: enhydris.activeTranslation,
  messages,
});

enhydris.VueApp = {
};

const app = Vue.createApp(enhydris.VueApp);
app.use(i18n);

app.component('user-menu-items', {
  template: '<li><a class="nav-link" href="#">{{ $t("Login") }}</a></li>',
});

app.mount('body');
