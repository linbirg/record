<template>
  <section class="real-app">
    <Chat v-if="chatVisible"></Chat>
    <div 
      class="toggle-btn"
      :class="{ collapsed: !chatVisible }"
      @click="toggleChat"
      :title="chatVisible ? '折叠 Chat' : '展开 Chat'"
    >
      <span v-if="chatVisible" class="icon">›</span>
      <span v-else class="icon dots">⋮</span>
    </div>
  </section>
</template>

<script>
import Chat from "./ChatList/chat";
import { mapState } from "vuex";

export default {
  name: 'RightSide',
  components: {
    Chat,
  },
  computed: {
    ...mapState(['chatVisible']),
  },
  methods: {
    toggleChat() {
      this.$store.commit('setChatVisible', !this.chatVisible);
    },
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

.toggle-btn {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 56px;
  background: rgba(156, 163, 175, 0.25);
  border-radius: 4px 0 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: rgba(59, 130, 246, 0.25);

    .icon {
      color: #3b82f6;
    }
  }

  .icon {
    font-size: 20px;
    color: #9ca3af;
    line-height: 1;
    font-weight: 600;
  }

  .dots {
    font-size: 18px;
    font-weight: 400;
  }
}
</style>
