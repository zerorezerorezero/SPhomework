#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

int main() {
    // === 1. open + write：開啟（或建立）檔案並寫入 ===
    int fd = open("hello.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open 寫入檔失敗");
        return 1;
    }

    char *msg = "Hello, 這是用 write 寫入的內容！\n";
    write(fd, msg, strlen(msg));
    printf("已寫入 %lu 個位元組到 hello.txt (fd = %d)\n", strlen(msg), fd);
    close(fd);

    // === 2. open + read：讀取剛剛寫入的檔案 ===
    fd = open("hello.txt", O_RDONLY);
    if (fd < 0) {
        perror("open 讀取檔失敗");
        return 1;
    }

    char buffer[128] = {0};
    ssize_t n = read(fd, buffer, sizeof(buffer) - 1);
    if (n > 0) {
        printf("從檔案讀到 %zd 個位元組：%s", n, buffer);
    }
    close(fd);

    return 0;
}
