const prop = {
  state: {
    prop: {
      default_model: "mrcnn",
      default_plugin: "coco",
      nocache: {
        form_left: 0,
        form_top: 0,
        show_label_table: false,
      },
    },
  },
  mutations: {
    updateProp(state, payload) {
      Object.assign(state.prop, payload);
    },
    updatePropNocache(state, payload) {
      if (state.prop.nocache) {
        Object.assign(state.prop.nocache, payload);
      } else {
        state.prop.nocache = payload;
      }
    },
  },
};

export default prop;
