CC=gcc
CFLAGS=
LDFLAGS=-lzmq
EXEC=reachy_client

all: $(EXEC)

hello: reachy_client.o
	$(CC) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm -rf *.o $(EXEC)
