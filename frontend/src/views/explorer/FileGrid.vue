<template>
  <div class="file-grid">
    <!-- File viewer menu -->
    <div class="file-toolbox">
      <a-checkbox
        :indeterminate="indeterminate"
        :checked="checkAll"
        @change="onCheckAllChange"
      >{{$t('all.select_all')}}</a-checkbox>
    </div>
    <a-divider />

    <a-checkbox-group :value="checkedList">
      <div class="file-grid-flex">
        <!-- Card -->
        <a-card
          class="file-card"
          v-for="item in data"
          :alt="item.fullname"
          :hoverable="true"
          :key="`${item.type}-${item.name}`"
          @dblclick="goto(item, $event)"
        >
          <a-checkbox slot="title" :value="`${item.type}-${item.id}`" @change="checkChange">
            <a-tooltip v-if="item.fullname!=item.title" :title="item.fullname">{{item.title}}</a-tooltip>
            <span v-else>{{item.title}}</span>
          </a-checkbox>

          <!-- Image -->
          <img v-if="item.thumb" class="grid-thumb" :alt="item.fullname" :src="item.thumb" />
          <img v-else class="grid-icon" :alt="item.fullname" :src="item.icon" />

          <a-icon slot="extra" type="down-circle" />
        </a-card>
      </div>
    </a-checkbox-group>
  </div>
</template>

<script>
const defaultCheckedList = [];

export default {
  data() {
    return {
      checkAll: false,
      checkedList: defaultCheckedList,
      indeterminate: false,
      lastShiftValue: undefined
    };
  },
  components: {
  },
  computed: {},
  props: ["data"],
  methods: {
    goto(target, event) {
      this.$emit("goto", target, event);
    },
    clearCheck() {
      const vm = this;
      vm.checkedList.splice(0, vm.checkedList.length);
      Object.assign(vm, {
        indeterminate: false,
        checkAll: false
      });
    },
    onCheckAllChange(e) {
      const vm = this;
      vm.checkedList.splice(0, vm.checkedList.length);
      if (e.target.checked) {
        for (let i in vm.data) {
          vm.checkedList.push(`${vm.data[i].type}-${vm.data[i].id}`);
        }
      }
      Object.assign(vm, {
        indeterminate: false,
        checkAll: e.target.checked
      });

      // emit
      vm.$emit("check", vm.checkedList, e);
    },
    checkChange(e) {
      const vm = this;
      const checkedSet = new Set(vm.checkedList);

      // deal with shift
      if (e.nativeEvent.shiftKey) {
        if (vm.lastShiftValue === undefined) {
          vm.lastShiftValue = e.target.value;
        } else {
          // add all selected
          const start = Math.min(e.target.value, vm.lastShiftValue);
          const end = Math.max(e.target.value, vm.lastShiftValue);
          for (let i = start; i <= end; i++) {
            if (e.target.checked) {
              checkedSet.add(i.toString());
            } else {
              checkedSet.delete(i.toString());
            }
          }
        }
      } else {
        vm.lastShiftValue = undefined; // clear shift value
      }
      if (e.target.checked) {
        checkedSet.add(e.target.value.toString());
      } else {
        checkedSet.delete(e.target.value.toString());

        vm.lastShiftValue = undefined; // clear shift value
      }

      // update status
      vm.checkedList.splice(0, vm.checkedList.length);
      checkedSet.forEach(value => {
        vm.checkedList.push(value);
      });
      const length = vm.checkedList.length;
      Object.assign(vm, {
        indeterminate: 0 < length && length < vm.data.length,
        checkAll: length === vm.data.length
      });

      // emit
      vm.$emit("check", vm.checkedList, e);
    }
  }
};
</script>


<style>
.file-grid-flex {
  max-height: calc(100vh - 320px);
  overflow: auto;
  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
}

.ant-card-head {
  min-height: 30px;
  height: 30px;
  padding: 0 12px;
}

.ant-card-head-wrapper {
  height: 30px;
}

.ant-card-head-title {
  padding: 4px 0;
}

.ant-card-hoverable {
  cursor: auto;
  border-radius: 5px;
}

.ant-card-hoverable:hover {
  border: 1px solid #80cef8;
  background-color: #e1eaf5;
}

.ant-card-hoverable:hover .ant-card-head {
  border-bottom-color: #80cef8;
}

.file-card {
  width: 150px;
  margin: 0 0 10px 10px;
}

.file-card > .ant-card-body {
  height: 110px;
  text-align: center;
  padding: 5px;
}

.grid-icon {
  width: 100%;
  max-height: 100px;
  max-width: 100px;
}

.grid-thumb {
  max-height: 100px;
  max-width: 140px;
}
</style>