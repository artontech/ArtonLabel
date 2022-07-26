<template>
  <div class="overview">
    <div class="file-container">
      <div class="secondary-menu">
        <!-- Breadcrumb -->
        <a-breadcrumb :routes="breadcrumb">
          <a-breadcrumb-item href></a-breadcrumb-item>
          <template slot="itemRender" slot-scope="{ route }">
            <a-icon v-if="route.icon != null" :type="route.icon" />&nbsp;
            <a @click="goto(route, $event)">{{ route.label }}</a>
          </template>
        </a-breadcrumb>

        <!-- Switch view -->
        <a class="secondary-menu-right" @click="switchFileView">
          <a-icon
            v-if="file_view == 'grid'"
            type="unordered-list"
            :style="{ fontSize: '16px' }"
          />
          <a-icon
            v-else-if="file_view == 'list'"
            type="appstore"
            :style="{ fontSize: '16px' }"
          />
        </a>
      </div>

      <!-- File viewer -->
      <FileGrid
        ref="fileGrid"
        v-if="file_view == 'grid'"
        :data="data"
        @check="check"
        @goto="goto"
      />
      <FileList
        ref="fileList"
        v-else-if="file_view == 'list'"
        :data="data"
        @check="check"
        @goto="goto"
      />

      <!-- Pagination -->
      <a-pagination
        class="file-pagination"
        size="small"
        show-quick-jumper
        show-size-changer
        :hideOnSinglePage="false"
        :current="page_no"
        :pageSize="page_size"
        :pageSizeOptions="['5', '15', '30', '60']"
        :total="total"
        :show-total="(total) => `Total ${total}`"
        @change="page1Change"
        @showSizeChange="page1Change"
      />
    </div>
  </div>
</template>

<script>
import options from "@/config/request";

const data = [];
const breadcrumb_home = {
  id: 0,
  type: "breadcrumb",
  icon: "home",
  label: "home",
  breadcrumbName: "home",
  children: [],
  page_no: 1,
};
export default {
  beforeMount() {
    const vm = this;
    vm.setting = vm.$store.state.setting;
  },
  components: {
    FileGrid: () => import("./FileGrid"),
    FileList: () => import("./FileList"),
  },
  data() {
    return {
      breadcrumb: [breadcrumb_home],
      checked: null,
      setting: null,
      data,
      file_view: "grid",
      page_no: 1,
      page_size: 15,
      total: 0,
    };
  },
  methods: {
    check(checked) {
      const vm = this;

      vm.checked = null;
      if (checked.length > 0) {
        vm.checked = checked;
      }
    },
    goto(target, event) {
      event;
      const routeData = this.$router.resolve({
        path: "/editor",
        query: {
          filename: target.fullname,
        },
      });
      window.open(routeData.href, "_blank");
    },
    list() {
      const vm = this;

      // Sending request
      const workspace = vm.setting.workspace;
      const body = {
        workspace,
        thumb: vm.setting.showthumb,
        page_no: vm.page_no,
        page_size: vm.page_size,
      };
      const onError = () => {
        console.log(`[Error] failed to overview workspace ${body.current}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/workspace/overview`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.data.splice(0, vm.data.length);
              data.list?.forEach((obj) => {
                obj.icon = `http://${vm.setting.address}${obj.icon}`;
                obj.thumb = `http://${vm.setting.address}/io/file?workspace=${workspace}&filename=${obj.fullname}`;

                // Add more attr
                if (obj.fullname?.length > 6) {
                  obj.title = `${obj.fullname.slice(0, 6)}...`;
                } else {
                  obj.title = obj.fullname;
                }
                vm.data.push(obj);
              });

              vm.total = data.total ? data.total : 0;
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    page1Change(page, pageSize) {
      const vm = this;
      vm.page_no = page;
      vm.page_size = pageSize;
      vm.list();
    },
    switchFileView() {
      const vm = this;

      // on view switch
      if (vm.file_view == "grid") {
        vm.$refs.fileGrid.clearCheck();
        vm.file_view = "list";
      } else {
        vm.$refs.fileList.clearCheck();
        vm.file_view = "grid";
      }
    },
  },
  mounted() {
    this.list();
  },
};
</script>

<style>
.ant-divider-horizontal {
  margin: 12px 0;
}

.file-container {
  margin-top: 8px;
}

.file-toolbox {
  margin-top: 8px;
}

.icon {
  max-height: 80px;
}

.secondary-menu {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.file-pagination {
  position: absolute;
  left: 50%;
  bottom: 5px;
  transform: translate(-50%, 0%);
}
</style>
