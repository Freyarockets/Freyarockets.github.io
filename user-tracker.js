class GameUserTracker {
    constructor() {
        this.activeUsers = {};
    }

    addUser(userId, ip) {
        this.activeUsers[userId] = ip;
    }

    removeUser(userId) {
        delete this.activeUsers[userId];
    }

    displayActiveUsers() {
        console.log('Active Game Users:');
        for (const user in this.activeUsers) {
            console.log(`User: ${user}, IP Address: ${this.activeUsers[user]}`);
        }
    }
}

// Example usage:
const userTracker = new GameUserTracker();
userTracker.addUser('player1', '192.168.1.1');
userTracker.displayActiveUsers();