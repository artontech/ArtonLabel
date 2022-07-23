<template>
  <div class="file-list">
    <!-- Table -->
    <a-table
      rowKey="fullname"
      tableLayout="fixed"
      :row-selection="{
        selectedRowKeys: selectedRowKeys,
        onChange: onSelectChange,
      }"
      :columns="columns"
      :data-source="data"
      :bordered="false"
      :pagination="false"
    >
      <span slot="icon" slot-scope="item">
        <!-- Image -->
        <img
          v-if="item.thumb"
          class="list-thumb"
          :alt="item.fullname"
          :src="item.thumb"
        />
        <img v-else class="list-icon" :alt="item.fullname" :src="item.icon" />
      </span>

      <span slot="name" slot-scope="item">
        <a-tooltip :title="item.fullname">
          <a @click="goto(item, $event)">{{ item.fullname }}</a>
        </a-tooltip>
      </span>

      <span slot="tags" slot-scope="item">
        <a-tag
          v-for="tag in item.tags"
          :key="`${item.name}${tag.key}:${tag.value}`"
          :color="'geekblue'"
          >{{ `${tag.key}:${tag.value}` }}</a-tag
        >
      </span>

      <span slot="action">
        <a-icon type="down-circle" />
      </span>
    </a-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      columns: [],
      selectedRowKeys: [],
    };
  },
  beforeMount() {
    const vm = this;

    // Table columns
    const columns = [
      {
        title: vm.$i18n.t("all.icon"),
        key: "icon",
        scopedSlots: { customRender: "icon" },
        ellipsis: true,
        width: 100,
        align: "center",
      },
      {
        title: "Name",
        key: "name",
        scopedSlots: { customRender: "name" },
        ellipsis: true,
        align: "left",
      },
      {
        title: "Tags",
        key: "tags",
        scopedSlots: { customRender: "tags" },
      },
      {
        title: "Size",
        key: "size",
        dataIndex: "attr.size",
        width: 100,
      },
      {
        title: "Action",
        key: "action",
        scopedSlots: { customRender: "action" },
        align: "right",
        width: 100,
      },
    ];
    columns.forEach((item) => {
      vm.columns.push(item);
    });
  },
  components: {
  },
  computed: {},
  props: ["data"],
  methods: {
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    moveto(target, event) {
      this.$emit("moveto", target, event);
    },
    clearCheck() {
      this.selectedRowKeys = [];
    },
    onChange(e) {
      this.$emit("onChange", e);
    },
    onSelectChange(selectedRowKeys, e) {
      const vm = this;
      vm.selectedRowKeys = selectedRowKeys;

      let checked = [];
      vm.selectedRowKeys.forEach((i) => {
        checked.push(`${vm.data[i].type}-${vm.data[i].id}`);
      });

      // emit
      vm.$emit("check", checked, e);
    },
  },
};
</script>


<style>
.file-list {
  max-height: calc(100vh - 250px);
  overflow: auto;
  padding-top: 10px;
}

.list-icon {
  max-height: 80px;
  max-width: 100px;
}

.list-thumb {
  max-height: 80px;
  max-width: 100px;
}
</style>