from enum import Enum
import openai
import tiktoken

# オレオレChatGPT

class Role(Enum):
    """
    メッセージのロールを表す列挙型
    """
    system = "system"
    user = "user"
    assistant = "assistant"

class Model(Enum):
    """
    モデルの列挙型
    """
    gpt35 = "gpt-3.5-turbo-0613"
    gpt35_16k = "gpt-3.5-turbo-16k-0613"
    gpt4 = "gpt-4-0613"
    gpt4_32k = "gpt-4-32k-0613"

class Message:
    """
    メッセージのクラス
    メッセージごとにロールと内容とトークンを保持する
    """

    def __init__(self, role: Role, content: str, token: int = 0):
        self.role: Role = role
        self.content: str = content
        self.calc_token()

    def msg2dict(self) -> dict:
        return {"role": self.role.name, "content": self.content}

    def set_token(self, token: int) -> None:
        self.token = token

    def msg2str(self) -> str:
        return f"{self.role.name} : {self.content}"

    def __str__(self) -> str:
        return self.msg2str()

    def calc_token(self,model:Model=Model.gpt35) -> None:
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model.value)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        self.token = len(encoding.encode(self.content))


class Response:
    """
    レスポンスのクラス
    必要な情報を雑にまとめる
    """

    def __init__(self, response: dict):
        self.choices: dict = response.get("choices", None)
        if self.choices:
            self.messages: list[Message] = [Message(Role(
                choice["message"]["role"]), choice["message"]["content"])for choice in self.choices]
        self.created: int | None = response.get("created", None)
        self.id: str | None = response.get("id", None)
        self.model: str | None = response.get("model", None)
        self.completeion_tokens: int | None = response["usage"].get(
            "completion_tokens", None)
        self.prompt_tokens: int | None = response["usage"].get(
            "prompt_tokens", None)
        """
        print(self.choices)
        print(self.messages)
        print(self.created)
        print(self.id)
        print(self.model)
        print(self.completeion_tokens)
        print(self.prompt_tokens)
        """


class Chat:
    """
    チャットのクラス
    """

    def __init__(self, API_KEY: str, organization: str | None = None, model: Model = Model.gpt35, TOKEN_LIMIT: int = 4096, REPLY_TOKEN: int =1024, n: int = 1) -> None:
        self.organization: str | None = organization
        self.history: list[Message] = []
        self.model: Model = model
        self.TOKEN_LIMIT: int = TOKEN_LIMIT
        self.n: int = n
        self.API_KEY: str = API_KEY
        self.REPLY_TOKEN: int = REPLY_TOKEN

    def add(self, message: list[Message] | Message, role: Role = Role.user, output: bool = False) -> None:
        """
        トークログの末尾にメッセージを追加
        """

        if type(message) is str:
            message = Message(role, message)
            self.history.append(message)
            if output:
                print(message)
        elif type(message) is list:
            if output:
                for msg in message:
                    print(msg)
            self.history.extend(message)
        elif type(message) is Message:
            self.history.append(message)
            if output:
                print(message)
        else:
            raise Exception("can't add anything that is not a message")

    def completion(self, output: bool = False) -> Message:
        """
        現在の履歴の状態で返信を得る
        戻り値はMessaegクラス
        """
        response = self.create()
        completion_token = response.completeion_tokens
        reply: Message = response.messages[0]
        reply.set_token(completion_token)
        self.history.append(reply)
        if output:
            print(reply)
        return reply

    def send(self, message: str | Message, role: Role = Role.user, output: bool = False) -> Message:
        """
        メッセージを追加して送信して返信を得る
        messageがMessageクラスならそのまま、strならMessageクラスに変換して送信
        add+completionみたいな感じ
        戻り値はMessageクラス
        """
        if type(message) is str:
            message = Message(role, message)

        if self.get_now_token() + len(message.content) > self.TOKEN_LIMIT:
            # トークン超過しそうなら良い感じに間引くかエラーを吐く
            self.thin_out()

        self.add(message, output=output)
        reply = self.completion(output=output)
        self.history.append(reply)
        return reply
    
    def stream_send(self, message: str | Message, role: Role = Role.user):
        if type(message) is str:
            message = Message(role, message)

        if self.get_now_token() + len(message.content) > self.TOKEN_LIMIT:
            # トークン超過しそうなら良い感じに間引くかエラーを吐く
            self.thin_out()
        
        self.add(message)

        return openai.ChatCompletion.create(
            model=self.model.value,
            messages=self.make_log(),
            stream=True,
            n=self.n
        )


    def make_log(self) -> list[dict]:
        """
        メッセージインスタンスのリストをAPIに送信する形式に変換
        """
        return [hist.msg2dict() for hist in self.history]

    def get_now_token(self) -> int:
        """
        現在のトークン数を取得
        """
        return sum([x.token for x in self.history])

    def thin_out(self, new_token:int=0) -> None:
        """
        トークログをTOKEN_LIMITに基づいて8割残すように先頭から消す
        引数nで減らす分のトークン数を指定
        """
        before_token = self.get_now_token()

        # print(now_token, new_token, self.TOKEN_LIMIT - REPLY_TOKEN)
        remove_token = 0
        remove_index = 0
        while before_token - remove_token + new_token > self.TOKEN_LIMIT - self.REPLY_TOKEN - 200:
            remove_token += self.history[remove_index].token
            remove_index += 1
        self.history = self.history[remove_index:]

    def create(self) -> Response:
        """
        openaiのAPIを叩く
        """
        openai.api_key = self.API_KEY
        if self.organization:
            openai.organization = self.organization
        log = self.make_log()
        # print(log)
        response = openai.ChatCompletion.create(
            model=self.model.value,
            messages=log,
            n=self.n
        )
        return Response(response)

    def get_history(self) -> str:
        """
        会話ログをテキスト化
        """
        text: str = ""

        for i, msg in enumerate(self.history):
            text += f"{i:03}:{msg.msg2str()[:-20]}\n"

        return text

    def remove(self, index: int) -> None:
        """
        ログの一部削除
        """
        if not 0 <= index < len(self.history):
            raise Exception("index out of range")
        self.history.remove(index)

    def reset(self):
        """
        ログの全削除
        """
        self.history = []

    def set_model(self, model: str) -> None:
        """
        モデルの変更
        """
        try:
            self.model = Model(model)
        except KeyError:
            raise Exception("無効なモデルです!: " + model)

    def set_token_limit_from_model(self) -> None:
        """
        モデルに応じてトークンの上限を変更
        """
        if self.model == Model.gpt35:
            self.TOKEN_LIMIT = 4096
        if self.model == Model.gpt35_16k:
            self.TOKEN_LIMIT = 16384
        if self.model == Model.gpt4:
            self.TOKEN_LIMIT = 8192
        if self.model == Model.gpt4_32k:
            self.TOKEN_LIMIT = 32768

        
    