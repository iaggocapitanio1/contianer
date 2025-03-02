<template>
  <div class="w-full mx-auto p-6 bg-white dark:bg-[#1c1c1c] shadow-none rounded-lg">
    <!-- Add Container Button -->
    <div v-if="props.requiredFilterFields.includes('addContainer')" class="mb-4 flex justify-start">
      <ActionButton
        label="Add Container"
        icon="pi pi-plus"
        class="p-button-success"
        @click="openContainer"
      />
    </div>

    <!-- Search Form -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      <!-- Radio Button Grid (3 Columns) -->
      <div class="md:col-span-6 grid grid-cols-3 gap-4">
        <div v-if="props.requiredFilterFields.includes('container')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="containerNumber" value="CONTAINER_NUMBER" />
          <label for="containerNumber" class="ml-2">Container #</label>
        </div>
        <div v-if="props.requiredFilterFields.includes('release')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="searchType" value="CONTAINER_RELEASE"/>
          <label for="searchType" class="ml-2">Release</label>
        </div>
        <div v-if="props.requiredFilterFields.includes('orderId')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="orderId" value="ORDER_ID" />
          <label for="orderId" class="ml-2">Order ID</label>
        </div>
      </div>

      <!-- Search Field & Buttons -->
      <div class="md:col-span-6 flex gap-2 items-end justify-end">
        <InputText
          v-if="props.requiredFilterFields.includes('searchContainer')"
          v-model="state.search"
          @blur="setReleaseNumber"
          class="w-full md:w-auto p-component p-inputtext-fluid"
          placeholder="Search containers"
        />
        <ActionButton
          icon="pi pi-search"
          class="p-button-primary p-2"
          :loading="state.quickSearchLoading || state.loading"
          @click="searchInventory"
        />
        <ActionButton
          icon="pi pi-refresh"
          class="p-button-secondary p-2"
          :loading="state.loading"
          @click="resetSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from "vue"
import InventoryService from "@/service/Inventory"
import InventoryApi from "@/api/inventory"
import { useToast } from "primevue/usetoast"
import ActionButton from "@/components/common/buttons/ActionButton.vue"
import { useUsers } from "@/store/modules/users"
import { useInventory } from "@/store/modules/inventory"
import { useAuth0 } from "@auth0/auth0-vue"
import cloneDeep from "lodash.clonedeep"

const emit = defineEmits(["openContainer", "setReleaseNumber"])
const props = defineProps({
  containerStatus: { type: String, default: "All" },
  requiredFilterFields: { type: Array, default: () => [] },
  resetFunc: { type: Function, default: () => {} },
  changeCategory: { type: Function, default: () => {} }
})

const usersStore = useUsers()
const inventoryStore = useInventory()
const inventoryService = new InventoryService()
const inventoryApi = new InventoryApi()
const toast = useToast()

const { user } = useAuth0()
const authUser = user

const container_default_search_type = computed(() => {
  return usersStore.cms?.default_container_search == "number"
    ? "CONTAINER_NUMBER"
    : "CONTAINER_RELEASE"
})

const state = reactive({
  searchType: container_default_search_type.value,
  search: "",
  quickSearchLoading: false,
  loading: false,
  selectedStatusIndex: 0,
  containers: []
})

const openContainer = () => {
  emit("openContainer")
}

const resetSearch = async () => {
  state.search = ""
  state.quickSearchLoading = false
  state.searchType = container_default_search_type.value
  state.containers = []
  await props.resetFunc()
  toast.add({
    severity: "info",
    summary: "Reset Search",
    detail: "Search reset",
    group: "br",
    life: 5000
  })
}

const searchInventory = async () => {
  state.quickSearchLoading = true
  state.containers = []
  state.search = state.search.trim()
  let urlStr = `searchBy=${state.searchType}&searchValue=${state.search}&searchStatus=${props.containerStatus}`

  const { error, data } = await inventoryApi.searchInventory(urlStr)
  if (error.value) {
    state.containers = []
  } else {
    state.containers = inventoryService.inventoryListToDtos(data.value)
    inventoryStore.setAvailableInventory([...state.containers])
  }

  state.quickSearchLoading = false
  toast.add({
    severity: "success",
    summary: "Success",
    detail: "Search complete",
    group: "br",
    life: 5000
  })
}

const setReleaseNumber = () => {
  if (state.searchType === "CONTAINER_RELEASE") {
    emit("setReleaseNumber", state.search)
  }
}
</script>
