const setting = {
  state: {
    setting: {
      address: "localhost:13312", // Api server address
      showthumb: true, // Show pic thumb or not
      workspace: "", // Workspace path
    },
  },
  mutations: {
    updateSetting(state, payload) {
      Object.assign(state.setting, payload);
    },
    updateSettingNocache(state, payload) {
      if (state.setting.nocache) {
        Object.assign(state.setting.nocache, payload);
      } else {
        state.setting.nocache = payload;
      }
    },
  },
};

export default setting;
