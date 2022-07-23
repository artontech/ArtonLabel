import Vue from "vue";
import Vuex from "vuex";
import persistedState from "vuex-persistedstate";

import setting from "./setting";

Vue.use(Vuex);

const options = {
  plugins: [
    persistedState({
      storage: {
        getItem: (key) => {
          return localStorage.getItem(key);
        },
        setItem: (key, value) => {
          let obj = JSON.parse(value);
          for (let item in obj) delete obj[item].nocache;
          localStorage.setItem(key, JSON.stringify(obj));
        },
        removeItem: (key) => {
          localStorage.removeItem(key);
        },
      },
    }),
  ],
  state: {
    ...setting.state,
  },
  mutations: {
    ...setting.mutations,
  },
};

const store = new Vuex.Store(options);

export default store;
