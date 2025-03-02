<template>
  <!-- 
    CustomButton Component
    ======================
    A reusable button component that extends PrimeVue's <Button>, inheriting all default properties while allowing custom styling and slot content.
    
    Props:
    - label (String): The button label (default: empty string).
    - onClick (Function): The function executed when the button is clicked (default: empty function to prevent errors).
    
    Features:
    - Supports default button properties via `v-bind="$attrs"`.
    - Accepts slot content to customize the button appearance.
    - Uses `p-button-rounded` for rounded styling.
    
    Example Usage:
    <CustomButton label="Submit" @click="handleSubmit" />
    <CustomButton @click="deleteItem">
      <i class="pi pi-trash"></i> Delete
    </CustomButton>
  -->

  <Button
    v-bind="$attrs"
    :class="cn('inline-flex items-center justify-center rounded-md text-sm',
     'font-medium transition-colors focus-visible:outline-none', 
     'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', 
     'disabled:pointer-events-none disabled:opacity-50 w-fit ',

         $attrs.class)" 
    :label="label"
    @click="onClick"
  >
    <slot></slot> <!-- Enables custom content inside the button -->
  </Button>
</template>


<script setup>
import { cn } from "@/utils/helpers";

defineProps({
  label: {
    type: String,
    default: "", // Avoids "undefined" labels
  },
  onClick: {
    type: Function,
    default: () => {}, // Ensures there's always a function
  },
});
</script>

