# OpenCode on Uniac

Deploy the OpenCode browser UI with password sign-in and a persistent coding
workspace. The default model is DeepSeek V4.1 Flash 1017 through OpenRouter.
The service runs one replica with 1 vCPU, 2 GiB RAM, and a 10 GiB volume.
Uniac meters compute and storage. OpenRouter bills model usage separately.

## Deploy

You need Git, Python 3, a running Docker daemon, a Uniac account, and an
OpenRouter API key. Install the Uniac CLI with Node.js 18 or later.

```sh
npm install -g @uniac/cli@0.3.34
git clone https://github.com/uniac-dev/opencode-on-uniac.git
cd opencode-on-uniac
uniac auth login
uniac auth status
uniac project create opencode-workspace
uniac link opencode-workspace
uniac plan
uniac deploy
uniac status
```

Sign in to your own Uniac account in the browser prompt. If you choose a
different project name, use it for both `project create` and `link`. Use the
HTTPS endpoint in the `uniac status` output.

If Docker runs under Colima or another non-default context, set the daemon
socket for the deploy command.

```sh
DOCKER_HOST="$(docker context inspect --format '{{.Endpoints.docker.Host}}')" uniac deploy
```

## Sign in and connect OpenRouter

The first start generates a password on the volume. Retrieve it into a private
local file.

```sh
(
  umask 077
  mkdir -p .private
  uniac exec opencode -- cat /data/server-password > .private/server-password
)
```

Open the HTTPS endpoint, choose **Use password**, and enter the password from
that file. The server address should match the endpoint shown by `uniac status`.
The OpenCode API username is `opencode`.

Create an API key in your own OpenRouter account. The following prompt writes
it to a file with mode 0600. The setup script passes the key through Uniac exec
standard input to OpenCode's native credential store on the volume.

```sh
(
  umask 077
  mkdir -p .private
  python3 -c 'import getpass; print(getpass.getpass("OpenRouter API key: "))' > .private/openrouter.key
)
python3 configure-openrouter.py --key-file .private/openrouter.key
```

Refresh OpenCode and start a new session. The composer should show **OpenRouter /
DeepSeek V4.1 Flash 1017**. The configured context and output limits are 65,536
and 2,048 tokens, respectively. Use the same setup command with a new key file
when renewing credentials.

## Verify workspace persistence

In a browser session, ask OpenCode to create `/data/workspace/hello.py` that
prints `hello from OpenCode`, then run it with `python3`. Check the tool output.
Refresh the page to reopen the conversation. To test container replacement,
run `uniac deploy` again in the linked project, reopen the conversation, and ask
OpenCode to rerun the existing file.

Use `/data/workspace` for your files. The `opencode.data` volume at `/data`
also stores sessions, configuration, the sign-in password, and provider
credentials. Redeploying the same service with the same volume preserves them.

## Source and image licenses

The [MIT license](LICENSE) covers this Uniac deployment wrapper and its
documentation. The Dockerfile builds from the public OpenCode 2.2.5
`linux/amd64` image pinned by digest. OpenCode carries its [own MIT
license](LICENSES/OpenCode-MIT.txt), and packaged dependencies retain their
respective licenses. The repository contains the build recipe and configuration
for a fresh deployment. [Upstream image](https://github.com/anomalyco/opencode/pkgs/container/opencode)
