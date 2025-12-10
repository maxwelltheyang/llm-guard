import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import org.jasypt.util.password.PasswordEncryptor;
import org.jasypt.util.password.PooledDigestPasswordEncryptor;

public class Main {

    private static final String CIPHER_SUITE = "AES/GCM/NoPadding";
    private static final int TAG_SIZE = 128;
    private static final int DEFAULT_ITERATION_COUNT = 2097152; // Increased iteration count for improved security
    private static final int SALT_SIZE = 32;

    public static void main(String[] args) {
        String configFilePath = System.getenv("config.file.path");
        if (configFilePath != null && !configFilePath.isEmpty()) {
            loadConfig(configFilePath);
        } else {
            // Use default or hardcoded configuration values
            String configFileContent = "key=secret-key\nsalt=generated-salt";
            storeConfig(configFileContent, "default-config.txt");
        }

        String username = "valid_username";
        String password = "password123";
        byte[] salt = generateSalt(username);
        Key key = deriveKey(password.getBytes(), salt);

        // Additional authentication factor (e.g., IP address and username combination)
        String additionalAuthenticationFactor = configureAdditionalAuthenticationFactor(username, getClientIP());
        if (additionalAuthenticationFactor != null && !additionalAuthenticationFactor.isEmpty()) {
            System.out.println("Additional Authentication Factor: " + additionalAuthenticationFactor);
        }

        String encryptedMessage = encryptMessage(key, "message-to-encrypt");
        byte[] decryptedData = decryptMessage(key, encryptedMessage);
        System.out.println("Decrypted Data: " + new String(decryptedData));
    }

    private static void loadConfig(String configFilePath) {
        try {
            Properties props = new Properties();
            props.load(new FileInputStream(configFilePath));
            // Load configuration values from the properties file
            String key = props.getProperty("key");
            String salt = props.getProperty("salt");
            System.out.println("Loaded configuration: " + key + ", " + salt);
        } catch (IOException e) {
            System.err.println("Error loading configuration file: " + e.getMessage());
        }
    }

    private static void storeConfig(String configFileContent, String configFileName) {
        try (FileWriter writer = new FileWriter(configFileName)) {
            writer.write(configFileContent);
            System.out.println("Configuration saved to file: " + configFileName);
        } catch (IOException e) {
            System.err.println("Error saving configuration file: " + e.getMessage());
        }
    }

    private static String configureAdditionalAuthenticationFactor(String username, String clientIP) {
        // Use a secure way to validate client-side data
        // For example, using digital signatures or other secure authentication mechanisms
        return username + "," + clientIP;
    }

    private static byte[] generateSalt(String username) {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[SALT_SIZE];
        random.nextBytes(salt);
        System.out.println("Generated salt for user: " + username);
        return salt;
    }

    private static Key deriveKey(byte[] password, byte[] salt) throws NoSuchAlgorithmException {
        PasswordEncryptor encryptor = new PooledDigestPasswordEncryptor();
        String hashedPassword = encryptor.sha512(password);
        // Use a more robust key derivation function, such as PBKDF2 or Argon2
        return new SecretKeySpec(hashedPassword.getBytes(), "AES");
    }

    private static String encryptMessage(Key key, String message) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE);
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSalt(""));
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedData = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedData);
    }

    private static byte[] decryptMessage(Key key, String encryptedMessage) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE);
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSalt(""));
        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        byte[] encryptedData = Base64.getDecoder().decode(encryptedMessage);
        return cipher.doFinal(encryptedData);
    }

    private static String getClientIP() {
        // Use a secure way to get the client's IP address
        // For example, using the X-Forwarded-For header in HTTP requests
        return "192.168.1.100";
    }
}
