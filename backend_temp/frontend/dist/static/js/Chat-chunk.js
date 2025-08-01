import { c as createElementBlock, a as createBaseVNode, t as toDisplayString, F as Fragment, r as renderList, e as withDirectives, v as vModelText, f as withKeys, o as openBlock, g as createTextVNode, _ as _export_sfc } from "./index-entry.js";
const _sfc_main = {
  props: {
    userID: Number
  },
  emits: ["temp-update-chat"],
  data() {
    return {
      chatTitle: "新聊天",
      chatID: 0,
      chatMessages: [],
      newMessage: "",
      status: "Complete"
    };
  },
  created() {
    this.$watch(
      () => this.$route.params.id,
      (newId, oldId) => {
        this.chatID = newId;
        this.chatMessages = [];
        this.newMessage = "";
        fetch("/chat-api/get-chat-message", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chatID: this.chatID })
        }).then((response) => response.json()).then((result) => {
          this.chatTitle = result["title"];
          this.chatMessages = result["result"].map(
            (row) => ({
              role: row["isUser"] ? "User" : "Assistant",
              message: row["message"].replace(/(\r\n|\r|\n)/g, "<br/>"),
              createdAt: new Date(row["lastUpdated"])
            })
          );
        }).catch((error) => console.error("Error obtaining chat: ", error));
      }
    );
  },
  async mounted() {
    this.chatID = this.$route.params.id;
    this.status = "Pending";
    await fetch("/chat-api/get-chat-message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chatID: this.chatID })
    }).then((response) => response.json()).then((result) => {
      this.chatTitle = result["title"];
      this.chatMessages = result["result"].map(
        (row) => ({
          role: row["isUser"] ? "User" : "Assistant",
          message: row["message"].replace(/(\r\n|\r|\n)/g, "<br/>"),
          createdAt: new Date(row["lastUpdated"])
        })
      );
      this.status = result["status"];
    }).catch((error) => console.error("Error obtaining chat: ", error));
    await this.loadingRemainingMessage();
  },
  methods: {
    // Send messages to be handled to the server.
    async sendMessage() {
      if (!this.newMessage) return;
      this.$emit("temp-update-chat");
      this.status = "Pending";
      const message = this.newMessage;
      this.newMessage = "";
      this.chatMessages.push({
        role: "User",
        message,
        createdAt: /* @__PURE__ */ new Date()
      });
      await fetch("/chat-api/send-message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chatID: this.chatID,
          message
        })
      }).then((response) => response.json()).then((result) => {
        this.chatMessages.push({
          role: "Assistant",
          message: result["message"].replace(/(\r\n|\r|\n)/g, "<br/>"),
          createdAt: new Date(result["createdAt"])
        });
        this.status = result["status"];
      }).catch((error) => console.error("Error sending message: ", error));
      await this.loadingRemainingMessage();
    },
    // If there are pending messages, we wait to get the messages from server.
    async loadingRemainingMessage() {
      while (this.status == "Pending") {
        await fetch("/chat-api/get-remaining-message", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chatID: this.chatID })
        }).then((response) => response.json()).then((result) => {
          this.chatMessages.push({
            role: "Assistant",
            message: result["message"].replace(/(\r\n|\r|\n)/g, "<br/>"),
            createdAt: new Date(result["createdAt"])
          });
          this.status = result["status"];
        });
      }
    }
  },
  computed: {
    // Messages that is sorted in ascending order by the creation time.
    // This will update upon when messages are sent.
    sortedMessages: {
      get() {
        return this.chatMessages.sort((a, b) => a.createdAt - b.createdAt);
      }
    }
  }
};
const _hoisted_1 = { class: "chat-page" };
const _hoisted_2 = ["innerHTML"];
const _hoisted_3 = { class: "main-input" };
const _hoisted_4 = ["disabled"];
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("main", _hoisted_1, [
    createBaseVNode("h2", null, toDisplayString(_ctx.chatTitle), 1),
    (openBlock(true), createElementBlock(Fragment, null, renderList(_ctx.sortedMessages, (message) => {
      return openBlock(), createElementBlock("p", null, [
        createTextVNode(toDisplayString(message.role) + ": ", 1),
        createBaseVNode("span", {
          innerHTML: message.message
        }, null, 8, _hoisted_2)
      ]);
    }), 256)),
    createBaseVNode("div", _hoisted_3, [
      withDirectives(createBaseVNode("input", {
        id: "message-input",
        type: "text",
        "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => _ctx.newMessage = $event),
        disabled: _ctx.status == "Pending",
        placeholder: "Test Message",
        onKeyup: _cache[1] || (_cache[1] = withKeys((...args) => _ctx.sendMessage && _ctx.sendMessage(...args), ["enter"]))
      }, null, 40, _hoisted_4), [
        [vModelText, _ctx.newMessage]
      ])
    ])
  ]);
}
const Chat = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", render], ["__scopeId", "data-v-5d619a8b"]]);
export {
  Chat as default
};
