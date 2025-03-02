<template>
  <div class="w-ful mx-auto p-6 bg-white dark:bg-[#1c1c1c] shadow-none rounded-lg ">
    
    <!-- Add Container Button -->
    <div v-if="requiredFilterFields.includes('addContainer')" class="mb-4 flex justify-start">
      <ActionButton
        label="Add Container"
        icon="pi pi-plus"
        class="p-button-success"
        @click="openContainer"
      />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      
      <!-- Radio Button Grid (Always 3 Columns) -->
      <div class="md:col-span-6 grid grid-cols-3 gap-4">
        <div v-if="requiredFilterFields.includes('container')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="containerNumber" value="CONTAINER_NUMBER" />
          <label for="containerNumber" class="ml-2">Container #</label>
        </div>
        <div v-if="requiredFilterFields.includes('release')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="searchType" value="CONTAINER_RELEASE"/>
          <label for="searchType" class="ml-2">Release</label>
        </div>
        <div v-if="requiredFilterFields.includes('orderId')" class="flex items-center">
          <RadioButton v-model="state.searchType" inputId="orderId" value="ORDER_ID" />
          <label for="orderId" class="ml-2">Order ID</label>
        </div>
      </div>

      <!-- Search Field & Buttons on the Right -->
      <div class="md:col-span-6 flex gap-2 items-end justify-end">
        <InputText
          v-if="requiredFilterFields.includes('searchContainer')"
          v-model="state.search"
          v-on:blur="setReleaseNumber"
          class="w-full md:w-auto p-component p-inputtext-fluid"
          placeholder="Search containers"
        />
        <ActionButton
          icon="pi pi-search"
          class="p-button-primary p-2"
          :loading="state.quickSearchLoading || state.loading"
          @click="searchInventory()"
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
  import { reactive, computed, watch, ref } from "vue"
  import InventoryService from "@/service/Inventory"
  import InventoryApi from "@/api/inventory"
  import { useToast } from "primevue/usetoast"

  // import { useDrivers } from "@/store/modules/drivers";
  import { useUsers } from "@/store/modules/users"
  import { useInventory } from "@/store/modules/inventory"
  import { isRentalsVisible } from "../../utils/allowedVisibilityForFeatures"
  import ActionButton from "@/components/common/buttons/ActionButton.vue"
  import { useAuth0 } from "@auth0/auth0-vue"
  import cloneDeep from "lodash.clonedeep"
  const emit = defineEmits(["openContainer", "setReleaseNumber"])
  const usersStore = useUsers()
  const inventoryStore = useInventory()
  const inventoryService = new InventoryService()
  const inventoryApi = new InventoryApi()
  const toast = useToast()

  const { user } = useAuth0()
  const authUser = user

  const categorys = computed(() => {
    let isProd = import.meta.env.PROD
    let accountId = usersStore?.cms?.account_id
    let isCMSRentalsEnabled = usersStore.cms?.feature_flags?.rentals_enabled
    let userEmail = usersStore?.currentUser.email
    let isRentalsFeatureVisible = isRentalsVisible(
      isProd,
      accountId,
      isCMSRentalsEnabled,
      userEmail
    )

    return isRentalsFeatureVisible
      ? [
          { name: "All", code: "ALL" },
          { name: "Sales", code: "PURCHASE" },
          { name: "Accessory Sales", code: "PURCHASE_ACCESSORY" },
          { name: "Rent to Own", code: "RENT_TO_OWN" },
          { name: "Rentals", code: "RENT" }
        ]
      : []
  })

  const container_default_search_type = computed(() => {
    return usersStore.cms?.default_container_search == "number"
      ? "CONTAINER_NUMBER"
      : "CONTAINER_RELEASE"
  })

  const { requiredFilterFields, containerStatus, resetFunc, changeCategory } =
    defineProps({
      containerStatus: {
        type: String,
        default: "All"
      },
      requiredFilterFields: {
        type: Array,
        default: () => []
      },
      resetFunc: {
        type: Function,
        default: () => {}
      },
      changeCategory: {
        type: Function,
        default: () => {}
      }
    })

  const openContainer = async (container) => {
    emit("openContainer", container)
  }
  const getContainerById = async (id) => {
    state.singleOrderLoading = true
    const { data, isLoading, error } = await inventoryApi.getInventoryById(id)

    if (error.value) {
      state.containerLoading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading order",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.containerLoading = false
      return inventoryService.dtoInventory(data.value)
    }
  }
  const resetSearch = async () => {
    state.search = ""
    state.quickSearchLoading = false
    state.searchType = container_default_search_type.value
    state.containers = []
    await resetFunc()
    toast.add({
      severity: "info",
      summary: "Reset Search",
      detail: "Search reset",
      group: "br",
      life: 5000
    })
  }

  const appendLineItemsToRentalHistory = (data) => {
    for (var i = 0; i < data.length; i++) {
      for (var j = 0; j < data[i].line_items.length; j++) {
        let rental_history = data[i].line_items[j].inventory.rental_history
        for (var x = 0; x < rental_history.length; x++) {
          rental_history[x].line_item = data[i].line_items[j]
          rental_history[x].line_item.order = data[i]
        }
      }
    }
    return data
  }

  const searchInventory = async () => {
    state.quickSearchLoading = true
    state.containers = []
    state.search = state.search.trim()
    let urlStr = `searchBy=${state.searchType}&searchValue=${state.search}&searchStatus=${containerStatus}`
    if (state.search) {
      urlStr = `searchBy=${state.searchType}&searchValue=${state.search}`
    }
    const { error, data } = await inventoryApi.searchInventory(urlStr)
    if (error.value) {
      data.value = []
    }
    state.containers = appendLineItemsToRentalHistory(
      inventoryService.removeOtherInventory(
        state.searchType,
        state.search,
        data.value
      )
    )
      .map((i) => inventoryService.orderToInventory(i))
      .flat(1)
      .filter((v, i, a) => a.findIndex((t) => t.id === v.id) === i)

    inventoryStore.setAvailableInventory([...state.containers])
    inventoryStore.setAllInventory([...state.containers])
    inventoryStore.setDeliveredInventory([...state.containers])
    inventoryStore.setAttachedInventory([...state.containers])
    inventoryStore.setDelinquentInventory([...state.containers])

    state.quickSearchLoading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Search complete",
      group: "br",
      life: 5000
    })
  }
  const currentStatus = computed(() => {
    return statusOptions.value[state.selectedStatusIndex]
  })

  const getInventory = async (skip = 0) => {
    if (skip === 0) {
      state.inventory = []
    }
    state.loading = true

    if (currentStatus.value === "Attached") {
      const mappedInventory = await getOrderInventory("Attached")
      inventoryStore.setAttachedInventory(mappedInventory)
      state.inventoryRawLength += mappedInventory.length
    } else if (currentStatus.value === "Delivered") {
      const mappedInventory = await getOrderInventory("Delivered")
      inventoryStore.setDeliveredInventory(mappedInventory)
      state.inventoryRawLength += mappedInventory.length
    }

    if (currentStatus.value === "Available" || currentStatus.value === "All") {
      const { data, error } = await inventoryApi.getInventoryByStatus(
        currentStatus.value,
        state.selectedCategory.code,
        skip
      )

      if (error.value) {
        state.loading = false
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error loading inventory",
          group: "br",
          life: 5000
        })
        return
      }

      if (currentStatus.value === "All") {
        const allInventory = [
          ...cloneDeep(inventoryStore.allInventory),
          ...inventoryService.inventoryListToDtos(data.value)
        ]
        inventoryStore.setAllInventory(allInventory)
      } else {
        const availableInventory = [
          ...cloneDeep(inventoryStore.availableInventory),
          ...inventoryService.inventoryListToDtos(data.value)
        ]
        inventoryStore.setAvailableInventory(availableInventory)
      }
    }
    state.loading = false
  }
  const statusOptions = computed(() => {
    return usersStore.cms?.inventory_status_options || []
  })

  const state = reactive({
    searchType: container_default_search_type.value,
    refreshKey: 0,
    ordersWithContainer: [],
    deleteLoading: false,
    search: "",
    quickSearchLoading: false,
    container: {},
    containers: [],
    containerDialog: false,
    containerDetailDialog: false,
    selectedAddButton: null,
    selectedStatusIndex: 0,
    loading: false,
    inventoryRawLength: 0,
    noteDialog: false,
    filters: {},
    selectedCategory: { name: "All", code: "ALL" }
  })
  const setReleaseNumber = () => {
    if (state.searchType == "CONTAINER_RELEASE")
      emit("setReleaseNumber", state.search)
  }
  watch(
    () => state.selectedCategory,
    async () => {
      //await changeCategory(state.selectedCategory);
    }
  )

  watch(
    () => state.searchType,
    async () => {
      setReleaseNumber()
    }
  )
</script>
