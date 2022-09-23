<template>
  <div class="editor">
    <div class="toolbox">
      <a-space direction="vertical">
        <span>
          {{ $t("all.model") }}:
          <a-select
            class="toolbox-child"
            size="small"
            :default-value="prop.default_model"
            @change="onSelect1Change"
          >
            <a-select-option value="mrcnn"> MRCNN </a-select-option>
            <a-select-option value="hrnet"> HRNET </a-select-option>
            <a-select-option value="mobilenet" disabled>
              MobileNet
            </a-select-option>
          </a-select>
        </span>
        <span>
          {{ $t("all.plugin") }}:
          <a-input
            class="toolbox-child"
            size="small"
            placeholder="Plugin"
            v-model="plugin"
          />
        </span>
        <span>
          <a-button
            type="primary"
            :loading="loading"
            @click="onButtonLoadModelClick"
          >
            {{ $t("app.load_model") }}
          </a-button>
          <a-divider type="vertical" />
          <a-button-group size="small">
            <a-button @click="onButtonPrevClick">
              {{ $t("app.pre_pic") }}
            </a-button>
            <a-button @click="onButtonNextClick">
              {{ $t("app.next_pic") }}
            </a-button>
          </a-button-group>
        </span>
        <a-divider />
        <float-form
          ref="form1"
          title="Label Form"
          :defaultLeft="250"
          :defaultTop="0"
        >
          <a-space direction="vertical">
            <span>
              {{ $t("app.draw") }}:
              <a-button-group>
                <a-button @click="onButtonDrawMaskClick">
                  {{ $t("app.draw_mask") }}
                </a-button>
                <a-button @click="onButtonDrawRoiClick">
                  {{ $t("app.draw_roi") }}
                </a-button>
              </a-button-group>
            </span>
            <a-table
              class="table-label"
              row-key="key"
              size="small"
              :columns="columns"
              :data-source="instances"
              :pagination="pagination"
              :row-selection="rowSelection"
            >
              <div class="textclip" slot="class" slot-scope="text">
                <a-tooltip>
                  <template slot="title">{{ text }}</template>
                  {{ text }}
                </a-tooltip>
              </div>
              <a-tooltip slot="scores" slot-scope="text">
                <template slot="title">{{ text }}</template>
                {{ text }}
              </a-tooltip>
            </a-table>
          </a-space>
        </float-form>
        <span>
          {{ $t("all.action") }}:
          <a-button-group>
            <a-button @click="showLabelTable">
              {{ $t("app.edit_label") }}
            </a-button>
          </a-button-group>
        </span>
      </a-space>
    </div>
    <div class="konva-container" :id="konvaContainerId"></div>
  </div>
</template>

<script>
import Konva from "konva";
// by default Konva prevent some events when node is dragging
// it improve the performance and work well for 95% of cases
// we need to enable all events on Konva, even when we are dragging a node
// so it triggers touchmove correctly
Konva.hitOnDragEnabled = true;
const freezeSizeNodeName = "freeze-size"; // 设置要冻结缩放的元素name: freezeSizeNodeName
var lastCenter = null;
var lastDist = 0;

import options from "@/config/request";
import FloatForm from "@/components/FloatForm.vue";

const columns = [
  {
    title: "Class",
    dataIndex: "class",
    key: "class",
    scopedSlots: { customRender: 'class' },
    width: "60%",
  },
  {
    title: "Scores",
    dataIndex: "scores",
    key: "scores",
    ellipsis: true,
    scopedSlots: { customRender: 'class' },
  },
];

export default {
  beforeMount() {
    const vm = this;
    vm.filename = vm.$route.query.filename;
    vm.prop = vm.$store.state.prop;
    vm.setting = vm.$store.state.setting;

    const { default_model, default_plugin } = vm.prop;
    if (default_model) vm.model = default_model;
    if (default_plugin) vm.plugin = default_plugin;
  },
  components: {
    FloatForm,
  },
  computed: {
    rowSelection() {
      const vm = this;
      return {
        onChange: (selectedRowKeys, selectedRows) => {
          selectedRows;
          selectedRowKeys;
        },
        onSelect: (record, selected, selectedRows) => {
          record;
          selected;

          vm.selectedInstanceKeys = [];
          selectedRows?.forEach((instance) => {
            vm.selectedInstanceKeys.push(instance.key);
          });
        },
        onSelectAll: (selected) => {
          vm.selectedInstanceKeys = [];
          if (selected) {
            vm.instances?.forEach((instance) => {
              vm.selectedInstanceKeys.push(instance.key);
            });
          }
        },
        getCheckboxProps: (record) => {
          return {
            props: {
              defaultChecked: false,
              disabled: record.name === "Disabled", // Column configuration not to be checked
              name: record.name,
            },
          };
        },
        columnWidth: 30,
        selectedRowKeys: vm.selectedInstanceKeys,
      };
    },
  },
  data() {
    return {
      konvaContainerId: "konva-container",
      filename: null,
      setting: null,
      stage: null,
      layer: null,
      maskGroup: null,
      roiGroup: null,
      width: 0,
      height: 0,
      model: null,
      plugin: null,
      loading: false,
      instances: [],
      columns,
      pagination: {
        position: "bottom",
        pageSize: 5,
      },
      prop: {},
      selectedInstanceKeys: [],
      classes: [],
    };
  },
  inject: ["reload"],
  methods: {
    async init() {
      const vm = this;
      const container = document.getElementById(vm.konvaContainerId);
      if (!container) return;

      vm.width = container.clientWidth;
      vm.height = container.clientHeight;

      if (!vm.stage) {
        vm.stage = new Konva.Stage({
          container: vm.konvaContainerId,
          draggable: true,
        });
        vm.stage.on("touchmove", vm.onTouchMove);
        vm.stage.on("touchend", () => {
          lastDist = 0;
          lastCenter = null;
        });
        vm.stage.on("wheel", vm.onWheel);
      }
      vm.stage.width(vm.width);
      vm.stage.height(vm.height);

      if (!vm.layer) {
        vm.layer = new Konva.Layer({
          id: "konva-layer",
        });
        vm.stage.add(vm.layer);
      } else {
        vm.layer.destroyChildren();
      }

      vm.maskGroup = new Konva.Group({
        x: 0,
        y: 0,
        draggable: false,
      });
      vm.layer.add(vm.maskGroup);

      vm.roiGroup = new Konva.Group({
        x: 0,
        y: 0,
        draggable: false,
      });
      vm.layer.add(vm.roiGroup);

      await vm.loadAnnotationConfig();

      const workspace = vm.setting.workspace;
      Konva.Image.fromURL(
        `http://${vm.setting.address}/io/file?workspace=${workspace}&filename=${vm.filename}`,
        async (img) => {
          img.setAttrs({
            width: img.attrs.image.naturalWidth,
            height: img.attrs.image.naturalHeight,
            x: 0,
            y: 0,
            draggable: false,
          });
          vm.layer.add(img);
          vm.rescalePicture(img);
          img.zIndex(0);
          vm.maskGroup.zIndex(1);
          vm.roiGroup.zIndex(2);

          await vm.loadAnnotation();
          if (vm.prop.nocache.show_label_table) vm.showLabelTable();
        }
      );
    },
    loadAnnotationConfig() {
      const vm = this;

      // Sending request
      const workspace = vm.setting.workspace;
      const body = {
        workspace,
      };
      const onError = () => {
        console.log(`[Error] failed to load annotation config ${body.image_name}`);
      };
      let promise = vm.$http
        .post(
          `http://${vm.setting.address}/annotation/loadConfig`,
          body,
          options
        )
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.classes.splice(0, vm.classes.length);
              data.classes?.forEach((cls) => {
                vm.classes.push(cls);
              });
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
      return promise;
    },
    loadAnnotation() {
      const vm = this;

      // Sending request
      vm.loading = true;
      const workspace = vm.setting.workspace;
      const body = {
        workspace,
        image_name: vm.filename,
      };
      const onError = () => {
        vm.loading = false;
        console.log(`[Error] failed to load annotation ${body.image_name}`);
      };
      let promise = vm.$http
        .post(`http://${vm.setting.address}/annotation/load`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.instances.splice(0, vm.instances.length);
              data.instances?.forEach((instance) => {
                vm.instances.push(instance);
                vm.selectedInstanceKeys.push(instance.key);
              });
              vm.loading = false;
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
      return promise;
    },
    loadMask(instance, info) {
      const vm = this;

      // Sending request
      const workspace = vm.setting.workspace;
      Konva.Image.fromURL(
        `http://${vm.setting.address}/annotation/loadMask?workspace=${workspace}&image_name=${vm.filename}&mask_name=${instance.mask}`,
        (img) => {
          img.setAttrs({
            id: `mask-${instance.key}`,
            width: img.attrs.image.naturalWidth,
            height: img.attrs.image.naturalHeight,
            x: 0,
            y: 0,
            draggable: false,
            opacity: info?.opacityMask ?? 0.5,
          });
          if (info?.color) {
            img.cache();
            img.filters([Konva.Filters.RGB]);
            const rgb = Konva.Util.getRGB(info.color);
            img.red(rgb.r);
            img.green(rgb.g);
            img.blue(rgb.b);
          }
          vm.maskGroup.add(img);
        }
      );
    },
    onClose() {
      const vm = this;
      if (vm.layer) {
        vm.layer.destroyChildren();
      }
    },
    onButtonLoadModelClick() {
      const vm = this;

      // Sending request
      vm.loading = true;
      const workspace = vm.setting.workspace;
      const body = {
        workspace,
        image_name: vm.filename,
        plugin_name: vm.plugin,
      };
      const onError = () => {
        vm.loading = false;
        console.log(`[Error] failed to detect ${body.image_name}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/${vm.model}/detect`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.loadAnnotation();
              vm.$store.commit("updateProp", {
                default_plugin: vm.plugin,
                default_model: vm.model,
              });
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    onButtonDrawMaskClick() {
      const vm = this;
      vm.clearMask();
      vm.selectedInstanceKeys?.forEach((key) => {
        const instance = vm.getInstance(key);
        const info = vm.getClassInfo(instance.class);
        vm.loadMask(instance, info);
      });
    },
    onButtonDrawRoiClick() {
      const vm = this;
      vm.clearRoi();
      vm.selectedInstanceKeys?.forEach((key) => {
        const instance = vm.getInstance(key);
        const roi = instance.roi;
        if (!roi || roi.length <= 0) return;

        const info = vm.getClassInfo(instance.class);
        var rect = new Konva.Rect({
          id: `roi-${instance.key}`,
          x: roi[0],
          y: roi[1],
          width: roi[2] - roi[0],
          height: roi[3] - roi[1],
          opacity: info?.opacityRoi ?? 0.9,
          stroke: info?.color ?? "white",
          strokeScaleEnabled: false,
          strokeWidth: 3,
        });
        vm.roiGroup.add(rect);
      });
    },
    onButtonPrevClick() {
      const vm = this;
      vm.getNext().then((data) => {
        if (data?.prev) {
          vm.$router.go("Editor", `filename=${data.prev}`);
          vm.reload();
        }
      });
    },
    onButtonNextClick() {
      const vm = this;
      vm.getNext().then((data) => {
        if (data?.next) {
          vm.$router.go("Editor", `filename=${data.next}`);
          vm.reload();
        }
      });
    },
    onSelect1Change(value) {
      const vm = this;
      vm.model = value;
    },
    onTouchMove(e) {
      function getDistance(p1, p2) {
        return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
      }

      function getCenter(p1, p2) {
        return {
          x: (p1.x + p2.x) / 2,
          y: (p1.y + p2.y) / 2,
        };
      }

      const vm = this;
      e.evt.preventDefault();
      const touch1 = e.evt.touches[0],
        touch2 = e.evt.touches[1];
      if (!touch1 || !touch2 || !vm.stage) return;

      // if the stage was under Konva's drag&drop
      // we need to stop it, and implement our own pan logic with two pointers
      if (vm.stage.isDragging()) {
        vm.stage.stopDrag();
      }

      const p1 = {
        x: touch1.clientX,
        y: touch1.clientY,
      };
      const p2 = {
        x: touch2.clientX,
        y: touch2.clientY,
      };

      if (!lastCenter) {
        lastCenter = getCenter(p1, p2);
        return;
      }
      const newCenter = getCenter(p1, p2);

      const dist = getDistance(p1, p2);

      if (!lastDist) {
        lastDist = dist;
      }

      // local coordinates of center point
      const pointTo = {
        x: (newCenter.x - vm.stage.x()) / vm.stage.scaleX(),
        y: (newCenter.y - vm.stage.y()) / vm.stage.scaleX(),
      };

      const scale = vm.stage.scaleX() * (dist / lastDist);

      vm.stage.scaleX(scale);
      vm.stage.scaleY(scale);

      // calculate new position of the stage
      const dx = newCenter.x - lastCenter.x;
      const dy = newCenter.y - lastCenter.y;

      const newPos = {
        x: newCenter.x - pointTo.x * scale + dx,
        y: newCenter.y - pointTo.y * scale + dy,
      };

      vm.stage.position(newPos);

      lastCenter = newCenter;
      lastDist = dist;
    },
    onWheel(e) {
      const vm = this;
      e.evt.preventDefault();
      const scale = e.evt.wheelDelta > 0 ? 1.05 : 1 / 1.05,
        scaleX = vm.stage.scaleX() * scale,
        scaleY = vm.stage.scaleY() * scale;
      const pointer = vm.stage.getPointerPosition();
      if (!pointer) return;
      const mousePointTo = {
        x: (pointer.x - vm.stage.x()) / vm.stage.scaleX(),
        y: (pointer.y - vm.stage.y()) / vm.stage.scaleY(),
      };
      const newPos = {
        x: pointer.x - mousePointTo.x * scaleX,
        y: pointer.y - mousePointTo.y * scaleY,
      };

      // Enable smoothing dynamically
      vm.layer.imageSmoothingEnabled(scaleX / vm.width < 0.01);

      vm.stage.scaleX(scaleX);
      vm.stage.scaleY(scaleY);
      vm.stage.position(newPos);

      vm.freezeNodeSize();
    },
    rescalePicture(img) {
      const vm = this;
      if (!vm.stage) {
        console.log(`${vm.id} rescalePicture failed, no stage`);
        return false;
      }
      const scaleX = vm.width / img.attrs.image.naturalWidth;
      const scaleY = vm.height / img.attrs.image.naturalHeight;
      const scale = Math.min(scaleX, scaleY);
      vm.stage.x(0);
      vm.stage.y(0);
      vm.stage.scaleX(scale);
      vm.stage.scaleY(scale);
      return true;
    },
    showLabelTable() {
      const vm = this;
      const nocache = vm.prop.nocache;
      vm.$refs.form1.toggleShow(nocache.form_left, nocache.form_top);
      vm.$store.commit("updatePropNocache", {
        show_label_table: true,
      });
    },
    freezeNodeSize() {
      const vm = this;

      // 冻结节点尺寸
      const nodes = vm.layer.find("." + freezeSizeNodeName);
      nodes.forEach((node) => {
        node.scaleX(1 / vm.stage.scaleX());
        node.scaleY(1 / vm.stage.scaleY());
      });
    },
    clearMask() {
      const vm = this;
      vm.maskGroup.destroyChildren();
    },
    clearRoi() {
      const vm = this;
      vm.roiGroup.destroyChildren();
    },
    getClassInfo(name) {
      const vm = this;
      for (let i = 0; i < vm.classes.length; i++) {
        const cls = vm.classes[i];
        if (name === cls.name) return cls;
      }
      return null;
    },
    getInstance(key) {
      const vm = this;
      for (let i = 0; i < vm.instances.length; i++) {
        const instance = vm.instances[i];
        if (key === instance.key) return instance;
      }
      return null;
    },
    getNext() {
      const vm = this;

      // Sending request
      const workspace = vm.setting.workspace;
      const body = {
        workspace,
        filename: vm.filename,
      };
      const onError = () => {
        throw `[Error] failed to get next file ${body.filename}`;
      };
      return vm.$http
        .post(`http://${vm.setting.address}/io/next`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              return data;
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
  },
  mounted() {
    const vm = this;
    vm.init();
  },
};
</script>

<style>
.editor {
  width: calc(100vw - 60px);
  height: calc(100vh - 110px);
  display: flex;
}

.toolbox {
  width: 20vw;
  min-width: 250px;
  max-width: 500px;
  height: 100%;
  margin-right: 5px;
}

.toolbox-child {
  width: 120px;
}

.konva-container {
  border-style: ridge;
  flex-grow: 1;
}

.table-label {
  max-width: 500px;
}

.ant-table-pagination.ant-pagination {
  float: right;
}

.ant-table-tbody .textclip {
  cursor: default;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ant-divider-horizontal {
  margin: 3px 0;
}
</style>
