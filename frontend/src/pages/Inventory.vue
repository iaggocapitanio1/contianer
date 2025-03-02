<template>
  <div>
    <div
      class="w-full flex justify-center md:justify-start items-center p-2 m-0 bg-0 dark:bg-900 gap-2"
    >
      <template :key="idx" v-for="(name, idx) in state.componentList">
        <div class="flex flex-row justify-center gap-4 w-fit-content ">
          <a
            v-ripple
            class="flex items-center p-1.5 p-button p-component"
            :class="{
              'p-button-primary': state.active === idx,
              'p-button-secondary': state.active !== idx
            }"
            @click="state.active = idx"
          >
            <span
              class="text-xl font-medium p-2"
              style="color: #f5f9ff"
              >{{ name }}</span
            >
          </a>
        </div>
      </template>
    </div>
    <inventory-table v-if="state.active === 0" class="mt-2"></inventory-table>
    <vendors-table
      v-if="state.active === 1 && $ability.can('read', 'inventory-vendors')"
      class="mt-2"
    ></vendors-table>
    <depots-table v-if="state.active === 2" class="mt-2"></depots-table>
  </div>
</template>

<script setup>
  // && $ability.can('read', 'inventory-depots')
  import { reactive, inject } from "vue"
  import InventoryTable from "@/components/inventory/InventoryTable.vue"
  import VendorsTable from "@/components/vendors/VendorsTable.vue"
  import DepotsTable from "@/components/depots/DepotsTable.vue"
  const $ability = inject("$ability")

  const state = reactive({
    active: 0,
    componentList: ["Inventory", "Vendors", "Depots"]
  })
</script>

<style></style>
