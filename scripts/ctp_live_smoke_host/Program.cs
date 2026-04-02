using System.Reflection;
using System.Text.Json;

sealed class SmokeConfig
{
    public string BrokerID { get; set; } = "";
    public string UserID { get; set; } = "";
    public string Password { get; set; } = "";
    public string ProductInfo { get; set; } = "";
    public string AppID { get; set; } = "";
    public string AuthCode { get; set; } = "";
    public string Pricer { get; set; } = "";
    public string Host { get; set; } = "";
    public byte ProviderId { get; set; }
    public int PostLoginDelaySeconds { get; set; }
    public string ManagedAssemblyDir { get; set; } = "";
    public string NativePackDir { get; set; } = "";
    public string[] Instruments { get; set; } = Array.Empty<string>();
}

sealed class SmokeState
{
    public TaskCompletionSource<bool> TdLoginReady { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource<bool> MdLoginReady { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource<string> FirstTick { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public bool SubscriptionSent { get; set; }
}

static class Program
{
    static readonly object SyncRoot = new();
    static Assembly? _ctpAssembly;
    static object? _native;
    static IntPtr _td;
    static IntPtr _md;
    static SmokeConfig? _config;
    static SmokeState? _state;

    static async Task<int> Main(string[] args)
    {
        var configPath = GetArgument(args, "--config");
        if (string.IsNullOrWhiteSpace(configPath))
        {
            Console.Error.WriteLine("Missing required argument: --config <path>");
            return 2;
        }

        var timeoutSeconds = int.TryParse(GetArgument(args, "--timeout-seconds"), out var parsedTimeout)
            ? parsedTimeout
            : 45;

        var config = LoadConfig(configPath);
        var validationErrors = Validate(config).ToArray();
        if (validationErrors.Length > 0)
        {
            Console.Error.WriteLine("Invalid config:");
            foreach (var error in validationErrors)
            {
                Console.Error.WriteLine($"- {error}");
            }
            return 2;
        }

        var state = new SmokeState();
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds));
        var assembly = LoadCtpAssembly();
        var native = Activator.CreateInstance(
            assembly.GetType("iTrading.Providers.CTPProviderSwig.CtpNativeLive", throwOnError: true)!,
            nonPublic: true
        ) ?? throw new InvalidOperationException("Could not create CtpNativeLive");

        _ctpAssembly = assembly;
        _native = native;
        _config = config;
        _state = state;
        _td = Invoke<IntPtr>(native, "TdCreate");
        _md = Invoke<IntPtr>(native, "MdCreate");

        try
        {
            var tdLoginCallback = BuildDelegate("iTrading.Providers.CTPProviderSwig.TdOnLoginCallback", nameof(OnTdLogin));
            var mdLoginCallback = BuildDelegate("iTrading.Providers.CTPProviderSwig.MdOnLoginCallback", nameof(OnMdLogin));
            var tickCallback = BuildDelegate("iTrading.Providers.CTPProviderSwig.MdOnTickCallback", nameof(OnTick));
            var tdDisconnected = BuildIntDelegate("iTrading.Providers.CTPProviderSwig.OnFrontDisconnectedCallback", nameof(OnTdDisconnected));
            var mdDisconnected = BuildIntDelegate("iTrading.Providers.CTPProviderSwig.OnFrontDisconnectedCallback", nameof(OnMdDisconnected));

            Invoke<object?>(native, "TdSetLoginCallback", _td, tdLoginCallback);
            Invoke<object?>(native, "TdSetFrontDisconnectedCallback", _td, tdDisconnected);
            Invoke<object?>(native, "MdSetLoginCallback", _md, mdLoginCallback);
            Invoke<object?>(native, "MdSetCallback", _md, tickCallback);
            Invoke<object?>(native, "MdSetFrontDisconnectedCallback", _md, mdDisconnected);

            Console.WriteLine($"TD init => {Invoke<int>(native, "TdInit", _td, config.Host)} [{config.Host}]");
            Console.WriteLine($"MD init => {Invoke<int>(native, "MdInit", _md, config.Pricer)} [{config.Pricer}]");

            if (!string.IsNullOrWhiteSpace(config.AuthCode) && !string.IsNullOrWhiteSpace(config.AppID))
            {
                Console.WriteLine($"TD authenticate => {Invoke<int>(native, "TdAuthenticate", _td, config.BrokerID, config.AppID, config.AuthCode)}");
            }

            Console.WriteLine($"TD login request => {Invoke<int>(native, "TdLogin", _td, config.BrokerID, config.UserID, config.Password)}");
            Console.WriteLine($"MD login request => {Invoke<int>(native, "MdLogin", _md, config.BrokerID, config.UserID, config.Password)}");

            using var _ = cts.Token.Register(() =>
            {
                state.TdLoginReady.TrySetCanceled(cts.Token);
                state.MdLoginReady.TrySetCanceled(cts.Token);
                state.FirstTick.TrySetCanceled(cts.Token);
            });

            await state.MdLoginReady.Task;
            var firstTick = await state.FirstTick.Task;
            Console.WriteLine($"SUCCESS first matching tick => {firstTick}");
            return 0;
        }
        catch (OperationCanceledException)
        {
            Console.Error.WriteLine($"Timed out after {timeoutSeconds} seconds without receiving a matching tick.");
            return 1;
        }
        finally
        {
            Invoke<object?>(native, "MdDispose", _md);
            Invoke<object?>(native, "TdDispose", _td);
        }
    }

    static void TrySubscribe()
    {
        if (_native is null || _config is null || _state is null)
        {
            return;
        }

        if (_state.SubscriptionSent || !_state.MdLoginReady.Task.IsCompletedSuccessfully)
        {
            return;
        }

        if (_config.PostLoginDelaySeconds > 0)
        {
            Console.WriteLine($"Post-login delay: {_config.PostLoginDelaySeconds}s");
            Thread.Sleep(TimeSpan.FromSeconds(_config.PostLoginDelaySeconds));
        }

        Console.WriteLine($"MD subscribe => {Invoke<int>(_native, "MdSubscribe", _md, _config.Instruments)} [{string.Join(", ", _config.Instruments)}]");
        _state.SubscriptionSent = true;
    }

    static SmokeConfig LoadConfig(string path)
    {
        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<SmokeConfig>(json)
            ?? throw new InvalidOperationException($"Could not deserialize config file: {path}");
    }

    static IEnumerable<string> Validate(SmokeConfig config)
    {
        if (string.IsNullOrWhiteSpace(config.BrokerID))
        {
            yield return "BrokerID is required";
        }
        if (string.IsNullOrWhiteSpace(config.UserID))
        {
            yield return "UserID is required";
        }
        if (string.IsNullOrWhiteSpace(config.Password))
        {
            yield return "Password is required";
        }
        if (string.IsNullOrWhiteSpace(config.Pricer))
        {
            yield return "Pricer is required";
        }
        if (string.IsNullOrWhiteSpace(config.Host))
        {
            yield return "Host is required";
        }
        if (config.Instruments.Length == 0)
        {
            yield return "At least one instrument is required";
        }
    }

    static string? GetArgument(IReadOnlyList<string> args, string name)
    {
        for (var i = 0; i < args.Count - 1; i++)
        {
            if (string.Equals(args[i], name, StringComparison.OrdinalIgnoreCase))
            {
                return args[i + 1];
            }
        }

        return null;
    }

    static Assembly LoadCtpAssembly()
    {
        var assemblyPath = Path.Combine(AppContext.BaseDirectory, "CTPProviderSwig.dll");
        if (!File.Exists(assemblyPath))
        {
            throw new FileNotFoundException("Missing CTPProviderSwig.dll in the smoke host output directory", assemblyPath);
        }
        return Assembly.LoadFrom(assemblyPath);
    }

    static Delegate BuildDelegate(string delegateTypeName, string handlerName)
    {
        var delegateType = _ctpAssembly!.GetType(delegateTypeName, throwOnError: true)!;
        var invokeMethod = delegateType.GetMethod("Invoke")!;
        var callbackType = invokeMethod.GetParameters()[0].ParameterType.GetElementType()!;
        var handler = typeof(Program).GetMethod(handlerName, BindingFlags.Static | BindingFlags.NonPublic)!.MakeGenericMethod(callbackType);
        return Delegate.CreateDelegate(delegateType, handler);
    }

    static Delegate BuildIntDelegate(string delegateTypeName, string handlerName)
    {
        var delegateType = _ctpAssembly!.GetType(delegateTypeName, throwOnError: true)!;
        var handler = typeof(Program).GetMethod(handlerName, BindingFlags.Static | BindingFlags.NonPublic)!;
        return Delegate.CreateDelegate(delegateType, handler);
    }

    static void OnTdDisconnected(int reason) => Console.WriteLine($"TD disconnected: reason={reason}");

    static void OnMdDisconnected(int reason) => Console.WriteLine($"MD disconnected: reason={reason}");

    static void OnTdLogin<T>(ref T response) where T : struct
    {
        var success = ReadBool(ref response, "IsSuccess");
        var errorId = ReadValue<int, T>(ref response, "ErrorId");
        var errorMessage = ReadValue<string, T>(ref response, "ErrorMessage") ?? "";
        Console.WriteLine($"TD login callback: success={success} error={errorId} message={errorMessage}");

        if (!success)
        {
            _state!.TdLoginReady.TrySetException(new InvalidOperationException($"TD login failed: {errorId} {errorMessage}"));
            return;
        }

        Invoke<int>(_native!, "TdConfirmSettlement", _td);
        _state!.TdLoginReady.TrySetResult(true);
        TrySubscribe();
    }

    static void OnMdLogin<T>(ref T response) where T : struct
    {
        var success = ReadBool(ref response, "IsSuccess");
        var errorId = ReadValue<int, T>(ref response, "ErrorId");
        var errorMessage = ReadValue<string, T>(ref response, "ErrorMessage") ?? "";
        Console.WriteLine($"MD login callback: success={success} error={errorId} message={errorMessage}");

        if (!success)
        {
            _state!.MdLoginReady.TrySetException(new InvalidOperationException($"MD login failed: {errorId} {errorMessage}"));
            return;
        }

        _state!.MdLoginReady.TrySetResult(true);
        TrySubscribe();
    }

    static void OnTick<T>(ref T tick) where T : struct
    {
        var symbol = ReadValue<string, T>(ref tick, "Symbol") ?? "";
        if (string.IsNullOrWhiteSpace(symbol))
        {
            return;
        }

        var last = ReadValue<double, T>(ref tick, "last");
        var bid = ReadValue<double, T>(ref tick, "bid");
        var ask = ReadValue<double, T>(ref tick, "ask");
        var ts = ReadValue<long, T>(ref tick, "ts_epoch_us");
        var line = $"{symbol} last={last} bid={bid} ask={ask} ts={ts}";
        Console.WriteLine($"TICK {line}");

        if (_config!.Instruments.Contains(symbol, StringComparer.OrdinalIgnoreCase))
        {
            _state!.FirstTick.TrySetResult(line);
        }
    }

    static TValue Invoke<TValue>(object target, string methodName, params object?[] args)
    {
        var method = target.GetType().GetMethod(methodName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
            ?? throw new MissingMethodException(target.GetType().FullName, methodName);
        var result = method.Invoke(target, args);
        if (typeof(TValue) == typeof(object))
        {
            return (TValue)result!;
        }
        return (TValue)result!;
    }

    static TValue ReadValue<TValue, TStruct>(ref TStruct value, string memberName) where TStruct : struct
    {
        object boxed = value;
        var type = boxed.GetType();
        var property = type.GetProperty(memberName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
        if (property is not null)
        {
            return (TValue)property.GetValue(boxed)!;
        }

        var field = type.GetField(memberName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
            ?? throw new MissingMemberException(type.FullName, memberName);
        return (TValue)field.GetValue(boxed)!;
    }

    static bool ReadBool<TStruct>(ref TStruct value, string memberName) where TStruct : struct
        => ReadValue<bool, TStruct>(ref value, memberName);
}
