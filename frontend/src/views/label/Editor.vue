<template>
  <div class="editor">
    <div class="toolbox">
      <a-space direction="vertical">
        <span>
          {{ $t("all.model") }}:
          <a-select
            class="toolbox-child"
            default-value="mrcnn"
            size="small"
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
        <a-button type="primary" :loading="loading" @click="onButton1Click">
          {{ $t("app.load_model") }}
        </a-button>
        <a-divider />
        <a-table
          size="small"
          :row-selection="rowSelection"
          :columns="columns"
          :data-source="instances"
          :pagination="pagination"
        ></a-table>
        <a-button-group>
          <a-button @click="onButton2Click">
            {{ $t("app.draw_mask") }}
          </a-button>
          <a-button @click="onButton3Click">
            {{ $t("app.draw_roi") }}
          </a-button>
        </a-button-group>
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
var lastCenter = null;
var lastDist = 0;

import options from "@/config/request";

const columns = [
  {
    title: "Class",
    dataIndex: "class",
    key: "class",
  },
  {
    title: "Scores",
    dataIndex: "scores",
    key: "scores",
    ellipsis: true,
  },
];

export default {
  beforeMount() {
    const vm = this;
    vm.filename = vm.$route.query.filename;
    vm.setting = vm.$store.state.setting;
  },
  components: {},
  computed: {
    rowSelection() {
      const vm = this;
      return {
        onChange: (selectedRowKeys, selectedRows) => {
          selectedRowKeys;
          vm.selectedInstances = selectedRows;
        },
        getCheckboxProps: (record) => ({
          props: {
            disabled: record.name === "Disabled User", // Column configuration not to be checked
            name: record.name,
          },
        }),
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
      model: "mrcnn",
      plugin: "coco",
      loading: false,
      instances: [],
      columns,
      pagination: {
        position: "bottom",
        pageSize: 5,
      },
      selectedInstances: null,
      classes: [],
    };
  },
  methods: {
    init() {
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
      }

      vm.maskGroup = new Konva.Group({
        opacity: 0.5,
        x: 0,
        y: 0,
        draggable: false,
      });
      vm.layer.add(vm.maskGroup);

      vm.roiGroup = new Konva.Group({
        opacity: 0.5,
        x: 0,
        y: 0,
        draggable: false,
      });
      vm.layer.add(vm.roiGroup);

      const workspace = vm.setting.workspace;
      Konva.Image.fromURL(
        `http://${vm.setting.address}/io/file?workspace=${workspace}&filename=${vm.filename}`,
        (img) => {
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
        }
      );

      // Sending request
      const body = {
        workspace,
      };
      const onError = () => {
        console.log(`[Error] failed to load annotation config ${body.image_name}`);
      };
      vm.$http
        .post(`http://${vm.setting.address}/annotation/loadConfig`, body, options)
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
      vm.$http
        .post(`http://${vm.setting.address}/annotation/load`, body, options)
        .then(
          (resp) => {
            const data = resp.body?.data;
            if (data && resp.body?.status === "success") {
              vm.instances.splice(0, vm.instances.length);
              data.instances?.forEach((instance) => {
                vm.instances.push(instance);
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
    },
    loadMask() {},
    onClose() {
      const vm = this;
      if (vm.layer) {
        vm.layer.destroyChildren();
      }
    },
    onButton1Click() {
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
            } else {
              onError();
            }
          },
          (error) => {
            onError(error);
          }
        );
    },
    onButton2Click() {
      const vm = this;
      vm.clearShape();
      console.log(vm.selectedInstances);
    },
    onButton3Click() {
      const vm = this;
      vm.clearShape();
      vm.selectedInstances?.forEach((instance) => {
        const roi = instance.roi;
        const color = vm.getClassInfo(instance.class)?.color;
        var rect = new Konva.Rect({
          x: roi[0],
          y: roi[1],
          width: roi[2] - roi[0],
          height: roi[3] - roi[1],
          fill: color ?? "black",
          stroke: "black",
          strokeWidth: 4,
        });
        vm.roiGroup.add(rect);
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

      vm.stage.scaleX(scaleX);
      vm.stage.scaleY(scaleY);
      vm.stage.position(newPos);
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
    clearShape() {
      const vm = this;
      vm.maskGroup.destroyChildren();
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
  flex-grow: 1;
}

.ant-table-pagination.ant-pagination {
  float: left;
}

.ant-divider-horizontal {
  margin: 3px 0;
}
</style>