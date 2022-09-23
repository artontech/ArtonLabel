<template>
  <transition>
    <div class="float-form" :style="position" v-show="visible">
      <div
        class="header"
        @mousedown="mousedown"
      >
        <span class="title">{{ title }}</span>
      </div>
      
      <div class="close" @click="toggleShow">×</div>
      <div class="content">
        <slot></slot>
      </div>
      
      <div
        class="mask"
        v-if="isMove"
        @mousemove="mousemove"
        @mouseup="mouseup"
        @mouseleave="mousemove"
      ></div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "float-form",
  data() {
    return {
      isMove: false,
      offsetX: 0,
      offsetY: 0,
      left: 0,
      top: 0,
      visible: false,
    };
  },
  computed: {
    position() {
      const vm = this;
      return `left: ${vm.left}px; top: ${vm.top}px;`;
    },
  },
  methods: {
    toggleShow() {
      const vm = this;
      if (vm.defaultLeft) vm.left = vm.defaultLeft;
      if (vm.defaultTop) vm.top = vm.defaultTop;
      vm.visible = !vm.visible;
      vm.showMask = false;
    },
    mousedown(event) {
      const vm = this;

      vm.offsetX = event.offsetX;
      vm.offsetY = event.offsetY;

      // 移动窗体时绘制不可见的遮罩，便于处理鼠标事件
      vm.isMove = true;
    },
    mousemove(event) {
      const vm = this;

      if (!vm.isMove) return;

      event.preventDefault();
      vm.left = event.clientX - vm.offsetX;
      vm.top = event.clientY - vm.offsetY;
    },
    mouseup() {
      const vm = this;
      vm.isMove = false;
    },
  },
  props: {
    defaultLeft: {
      type: Number,
      default: 0,
    },
    defaultTop: {
      type: Number,
      default: 0,
    },
    title: {
      type: String,
      default: "",
    },
  },
};
</script>

<style scoped>

.float-form {
  width: auto;
  height: auto;
  position: fixed;
  box-shadow: 0 0 5px 3px #95a5a6;
  z-index: 1;
}
.float-form .mask {
  width: 100vw;
  height: 100vh;
  position: fixed;
  left: 0px;
  top: 0px;
  z-index: 1;
}
.float-form .header {
  height: 30px;
  background-color: #bdc3c7;
  cursor: move;
  padding: 5px;
}
.float-form .title {
  text-align: center;
}
.float-form .close {
  position: absolute;
  right: 0;
  top: 0;
  line-height: 30px;
  font-size: 24px;
  cursor: pointer;
  display: block;
  width: 30px;
  height: 30px;
  text-align: center;
}

.v-enter, .v-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

.content {
  padding: 10px;
  background-color: white;
}

.v-enter-active, .v-leave-active {
  transition: all 0.5s ease;
}
</style>
