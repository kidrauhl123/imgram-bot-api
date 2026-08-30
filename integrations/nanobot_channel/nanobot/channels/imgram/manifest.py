"""imGram channel management contract."""

from nanobot.channels._manifest import GROUP_POLICIES, field, required
from nanobot.channels.contracts import ChannelSetupSpec
from nanobot.channels.plugin import ChannelPlugin

SETUP_SPEC = ChannelSetupSpec(
    fields={
        "token": field("secret"),
        "apiRoot": field(default="https://bot.premsir.com"),
        "proxy": field("secret"),
        "allowFrom": field("list"),
        "groupPolicy": field("enum", choices=GROUP_POLICIES, default="mention"),
        "replyToMessage": field("boolean", default=False),
        "streaming": field("boolean", default=True),
        "inlineKeyboards": field("boolean", default=False),
        "richMessages": field("boolean", default=False),
    },
    required=(required("token"),),
    official_url="https://github.com/kidrauhl123/imgram-bot-api",
)

PLUGIN = ChannelPlugin(
    name="imgram",
    display_name="imGram",
    runtime=f"{__package__}.runtime:ImgramChannel",
    setup=SETUP_SPEC,
    dependencies=(
        "python-telegram-bot[socks,webhooks]>=22.6,<23.0",
        "socksio>=1.0.0,<2.0.0",
        "python-socks[asyncio]>=2.8.0,<3.0.0; sys_platform != 'win32'",
    ),
)
