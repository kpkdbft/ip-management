<template>
    <v-container>
        <v-card class="mx-auto my-5 pa-5" max-width="1000px">
            <v-card-title class="text-h5">新規作成</v-card-title>
            <v-btn class="mb-2" color="primary" @click="handleEdit">
                New Item
            </v-btn>
            <v-dialog v-model="dialog" max-width="800px">
                <v-card>
                    <v-card-title>
                        <span class="text-h5">{{ formTitle }}</span>
                    </v-card-title>

                    <v-text-field
                        v-model="sendData.ip"
                        label="IPアドレス"
                        :error-messages="ipError"
                        placeholder="192.168.1.1"
                    ></v-text-field>
                    <v-text-field
                        v-model="sendData.hostname"
                        label="ホスト名"
                        placeholder="www.example.com"
                    ></v-text-field>
                    <v-select
                        v-model="sendData.device_type"
                        :items="locations"
                        label="機器種"
                    ></v-select>
                    <v-text-field
                        v-model="sendData.purpose"
                        label="用途"
                        placeholder="実験用"
                    ></v-text-field>
                    <v-select
                        v-model="sendData.admin"
                        :items="admins"
                        item-title="name"
                        :item-props="adminProps"
                        label="管理者"
                        :error-messages="adminError"
                    ></v-select>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            color="blue-darken-1"
                            variant="text"
                            @click="close"
                        >
                            Cancel
                        </v-btn>
                        <v-btn
                            color="blue-darken-1"
                            variant="text"
                            @click="handleSubmit"
                        >
                            Submit
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-dialog v-model="dialogDelete" max-width="500px">
                <v-card>
                    <v-card-title class="text-h5"
                        >本当に削除しますか?</v-card-title
                    >
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            color="blue-darken-1"
                            variant="text"
                            @click="closeDelete"
                            >Cancel</v-btn
                        >
                        <v-btn
                            color="blue-darken-1"
                            variant="text"
                            @click="deleteItemConfirm"
                            >OK</v-btn
                        >
                        <v-spacer></v-spacer>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-data-table
                :headers="ipHeaders"
                :items="ipAddresses"
                class="elevation-1 mt-5"
            >
                <template v-slot:[`item.status`]="{ item }">
                    <v-chip :color="getColor(item.status)">
                        {{ statusTxt(item.status) }}
                    </v-chip>
                </template>
                <template v-slot:[`item.action`]="{ item }">
                    <v-icon class="me-2" size="small" @click="handleEdit(item)">
                        mdi-pencil
                    </v-icon>
                    <v-icon
                        class="me-2"
                        size="small"
                        @click="handleDelete(item.id)"
                    >
                        mdi-delete
                    </v-icon>
                </template>
            </v-data-table>
        </v-card>
    </v-container>
</template>

<script>
export default {
    data() {
        return {
            serverURL: "http://localhost:8080",
            dialog: false,
            dialogDelete: false,
            index: 0,
            itemsPerPage: 6,
            pages: [
                { value: 5, title: "5" },
                { value: 10, title: "10" },
                { value: 20, title: "20" },
                { value: -1, title: "$vuetify.dataFooter.itemsPerPageAll" },
            ],
            ipHeaders: [
                {
                    title: "IPアドレス",
                    value: "ip",
                    sortable: true,
                    sort: (a, b) => {
                        return (
                            parseInt(a.split(".")[3]) -
                            parseInt(b.split(".")[3])
                        );
                    },
                    maxWidth: 100,
                },
                {
                    title: "ホスト名",
                    value: "hostname",
                    sortable: true,
                    maxWidth: 100,
                },
                {
                    title: "用途",
                    value: "purpose",
                    sortable: false,
                    maxWidth: 200,
                },
                {
                    title: "機器種",
                    value: "device_type",
                    sortable: true,
                    maxWidth: 140,
                },
                {
                    title: "管理者",
                    value: "admin",
                    sortable: true,
                    maxWidth: 100,
                },
                {
                    title: "状態",
                    value: "status",
                    sortable: true,
                    maxWidth: 80,
                    align: "center",
                },
                {
                    title: "編集",
                    value: "action",
                    sortable: false,
                    maxWidth: 80,
                    align: "center",
                },
            ],
            sendData: {
                ip: "",
                hostname: " ",
                purpose: " ",
                device_type: "",
                admin: "",
            },
            ipAddresses: [],
            locations: [
                "Raspberry Pi",
                "デスクトップPC",
                "ミニPC",
                "ネットワーク機器",
                "vm(host1)",
                "vm(host2)",
            ],
            admins: [],
            ipError: "",
            adminError: "",
        };
    },
    watch: {
        dialog(val) {
            val || this.close();
        },
        dialogDelete(val) {
            val || this.closeDelete();
        },
    },
    computed: {
        formTitle() {
            return this.index === -1 ? "New Item" : "Edit Item";
        },
    },
    methods: {
        async fetchIpAddresses() {
            const response = await fetch(`${this.serverURL}/api/ip-addresses`);
            const data = await response.json();
            this.ipAddresses = data;
            console.debug(this.ipAddresses);
        },
        async fetchAdmins() {
            const response = await fetch(`${this.serverURL}/api/admins`);
            const admins = await response.json();
            this.admins = admins;
        },
        adminProps(admin) {
            return {
                title: admin.name,
                subtitle: admin.grade,
            };
        },

        validateIp(ip) {
            const ipPattern =
                /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            return ipPattern.test(ip);
        },
        isExistIp(ip) {
            const index = this.ipAddresses.find((ipData) => ipData.ip === ip);
            return index !== undefined;
        },
        async handleSubmit() {
            if (!this.validateIp(this.sendData.ip)) {
                this.ipError = "不正なIPアドレスです。";
                return;
            }
            if (this.index == -1 && this.isExistIp(this.sendData.ip)) {
                this.ipError = "そのアドレスは既に存在します。";
                return;
            }
            if (!this.sendData.admin) {
                this.adminError = "管理者が入力されていません";
                return;
            }

            this.ipError = "";
            this.adminError = "";

            if (!this.sendData.hostname) {
                this.sendData.hostname = "なし";
            }
            if (!this.sendData.purpose) {
                this.sendData.purpose = "？";
            }
            const data = {
                ip: this.sendData.ip,
                hostname: this.sendData.hostname,
                purpose: this.sendData.purpose,
                device_type: this.sendData.device_type,
                admin: this.sendData.admin,
            };
            console.log(data);
            console.log(this.sendData);
            const method = this.index == -1 ? "POST" : "PUT";
            const response = await fetch(`${this.serverURL}/api/ip-addresses`, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
            const result = await response.json();
            console.log(result);
            this.resetSendData();
            this.fetchIpAddresses();
            this.close();
        },
        async handleEdit(item) {
            this.index = this.ipAddresses.indexOf(item);
            this.sendData = Object.assign({}, item);
            this.dialog = true;
        },
        close() {
            this.dialog = false;
        },
        async deleteItemConfirm() {
            const id = this.sendData.id;
            const response = await fetch(`${this.serverURL}/api/ip-addresses`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ id }),
            });
            const result = await response.json();
            console.log(result);
            this.fetchIpAddresses();
            this.closeDelete();
        },
        async handleDelete(id) {
            this.sendData.id = id;
            this.dialogDelete = true;
        },
        closeDelete() {
            this.dialogDelete = false;
            this.$nextTick(() => {
                this.resetSendData();
            });
        },
        resetSendData() {
            this.sendData.ip = "";
            this.sendData.hostname = " ";
            this.sendData.purpose = " ";
            this.sendData.device_type = "";
            this.sendData.admin = "";
        },
        getColor(status) {
            if (status) return "green";
            else return "red";
        },
        statusTxt(status) {
            if (status) return "Up";
            else return "Down";
        },
    },
    mounted() {
        this.fetchIpAddresses();
        this.fetchAdmins();
    },
};
</script>
