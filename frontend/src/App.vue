<template>
  <a-layout id="app">
    <MainHeader v-if="hasMainHeader" />
    <a-layout>
      <a-layout-sider v-if="hasMenu" width="200" style="background: #fff">
        <Menu />
      </a-layout-sider>
      <a-layout-content :style="{ margin: '16px 16px 0', overflow: 'initial' }">
        <a-card class="view-wrapper">
          <router-view />
        </a-card>
      </a-layout-content>
    </a-layout>
    <a-layout-footer v-if="hasFooter" :style="{ textAlign: 'center' }"
      >{{ $t("app.project_name") }} ©2022</a-layout-footer
    >
  </a-layout>
</template>

<script>
export default {
  components: {
    MainHeader: () => import("@/components/MainHeader.vue"),
  },
  computed: {
    hasFooter() {
      return ["Index", "Overview", "Editor"].indexOf(this.$route.name) > -1;
    },
    hasMainHeader() {
      return ["Index", "Overview", "Editor"].indexOf(this.$route.name) > -1;
    },
    hasMenu() {
      return [""].indexOf(this.$route.name) > -1;
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}

.ant-card-body {
  padding: 12px;
}

.ant-layout-footer {
  padding: 9px 24px;
}

.view-wrapper {
  min-height: calc(100vh - 92px);
  max-height: calc(100vh - 92px);
}
</style>
