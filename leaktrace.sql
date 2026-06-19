-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 19 Jun 2026 pada 09.25
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `leaktrace`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `activity` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `audit_logs`
--

INSERT INTO `audit_logs` (`id`, `activity`, `created_at`) VALUES
(1, 'Admin login', '2026-06-19 07:01:09'),
(2, 'Admin login', '2026-06-19 07:06:14'),
(3, 'Admin login', '2026-06-19 07:22:58');

-- --------------------------------------------------------

--
-- Struktur dari tabel `distributions`
--

CREATE TABLE `distributions` (
  `id` int(11) NOT NULL,
  `document_id` int(11) NOT NULL,
  `recipient_name` varchar(100) NOT NULL,
  `fingerprint` varchar(255) NOT NULL,
  `distributed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `distributions`
--

INSERT INTO `distributions` (`id`, `document_id`, `recipient_name`, `fingerprint`, `distributed_at`) VALUES
(1, 1, 'Bagas', '6b53eafcd61311f7b4a1f198418e1e48c3f2be3be138e9ec42ea99321c83f3b0', '2026-06-18 16:40:15');

-- --------------------------------------------------------

--
-- Struktur dari tabel `documents`
--

CREATE TABLE `documents` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `original_hash` varchar(255) NOT NULL,
  `upload_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `documents`
--

INSERT INTO `documents` (`id`, `filename`, `original_hash`, `upload_date`) VALUES
(1, 'Laporan PKL TErbaru 01.docx', 'e4cbbb2c1530e16e57538e52547919ed3e9ee549b0a052e07178068505a0fa46', '2026-06-18 16:40:03');

-- --------------------------------------------------------

--
-- Struktur dari tabel `investigations`
--

CREATE TABLE `investigations` (
  `id` int(11) NOT NULL,
  `uploaded_file` varchar(255) NOT NULL,
  `detected_recipient` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `investigated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `investigations`
--

INSERT INTO `investigations` (`id`, `uploaded_file`, `detected_recipient`, `status`, `investigated_at`) VALUES
(1, 'Laporan PKL TErbaru 01.docx', 'Bagas', 'TERDETEKSI', '2026-06-18 16:40:37'),
(2, 'Laporan PKL TErbaru 01.docx', '-', 'TIDAK DITEMUKAN', '2026-06-18 16:41:07');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `distributions`
--
ALTER TABLE `distributions`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `documents`
--
ALTER TABLE `documents`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `investigations`
--
ALTER TABLE `investigations`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `distributions`
--
ALTER TABLE `distributions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `documents`
--
ALTER TABLE `documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `investigations`
--
ALTER TABLE `investigations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
