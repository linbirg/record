<template>
  <section class="real-app">
    <Chat></Chat>
  </section>
</template>
<script>
  import Chat from "./ChatList/chat";
  export default {
    components: {
      Chat,
    },
  };
</script>
<style lang="scss" scoped>
  .real-app {
    position: fixed;
    top: 72px;
    left: 1335px;
    width: 500px;
    height: calc(100vh - 72px - 20px);
    margin: 0 auto;
    font-size: 14px;
  }
</style>
