<template>
  <a-form
    class="config-form"
    :form="form"
    id="config-panel"
    labelAlign="left"
    @submit="handleSubmit"
  >
    <a-form-item>
      <a-input
        v-decorator="[
          'workspace',
          {
            initialValue: setting.workspace
          },
          {
            rules: [
              { required: true, message: $t('config_panel.msg_no_workspace') },
            ],
          },
        ]"
        :placeholder="$t('config_panel.workspace')"
      >
        <a-icon slot="prefix" type="folder" style="color: rgba(0, 0, 0, 0.25)" />
      </a-input>
    </a-form-item>
    <a-form-item>
      <a-input
        v-decorator="[
          'address',
          {
            initialValue: setting.address
          },
          {
            rules: [
              { required: true, message: $t('config_panel.msg_no_address') },
            ],
          },
        ]"
        type="address"
        :placeholder="$t('config_panel.address')"
      >
        <a-icon slot="prefix" type="link" style="color: rgba(0, 0, 0, 0.25)" />
      </a-input>
    </a-form-item>
    <a-form-item>
      <a-button type="primary" html-type="submit" class="config-form-button" :loading="btn1_loading">
        {{ $t("config_panel.config") }}
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script>
import options from "@/config/request";

export default {
  name: "ConfigPanel",
  beforeCreate() {
    const vm = this;
    vm.form = vm.$form.createForm(vm, { name: "normal_config" });
  },
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
    if (vm.$route.query.workspace) {
      vm.setting.workspace = vm.$route.query.workspace;
    }
  },
  data() {
    return {
      btn1_loading: false,
      setting: null,
    };
  },
  methods: {
    handleSubmit(e) {
      e.preventDefault();
      this.form.validateFields((err, values) => {
        if (err) return;
        const vm = this;
        const body = {
          ...values,
        };
        vm.btn1_loading = true;
        const onError = () => {
          vm.$message.error(vm.$i18n.t("config_panel.init_workspace_fail"));
          vm.btn1_loading = false;
        };
        vm.$http
          .post(`http://${values.address}/workspace/init`, body, options)
          .then((resp) => {
            vm.btn1_loading = false;
            if (resp.body.status === "success") {
              vm.$store.commit("updateSetting", values);
              vm.$router.go("Overview", ``);
            } else {
              onError();
            }
          }, onError);
      });
    },
  },
  props: {},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#config-panel {
  text-align: left;
}
#config-panel .config-form-forgot {
  float: right;
}
#config-panel .config-form-button {
  width: 100%;
}
#config-panel .config-form-register {
  text-align: center;
}
</style>
